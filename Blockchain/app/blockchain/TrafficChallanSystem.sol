// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TrafficChallanSystem {

    address public admin;

    mapping(address => bool) public officers;
    mapping(address => bool) public authorizedCameras;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    modifier onlyOfficer() {
        require(officers[msg.sender], "Not authorized officer");
        _;
    }

    modifier onlyCamera() {
        require(authorizedCameras[msg.sender], "Not authorized camera");
        _;
    }

    struct Vehicle {
        string plateNumber;
        address owner;
        bool exists;
    }

    // NEW — Better challan lifecycle management
    enum ChallanStatus {
        Pending,
        Paid,
        Cancelled,
        Disputed
    }

    struct Challan {
        uint256 challanId;

        string plateNumber;

        string violationType;

        string location;

        uint256 fineAmountPaise;

        string ipfsCID;

        bytes32 challanHash;

        uint256 violationTimestamp;

        uint256 blockchainTimestamp;

        ChallanStatus status;

        address createdBy;
    }

    uint256 public challanCounter;

    mapping(string => Vehicle) public vehicles;
    mapping(uint256 => Challan) public challans;

    // NEW — duplicate prevention
    mapping(bytes32 => bool) public processedViolations;

    uint256 public finePerKmhOver = 0.001 ether;

    event VehicleRegistered(string plate, address owner);
    event OfficerAdded(address officer);
    event CameraAuthorized(address camera);

    event ChallanIssued(
        uint256 challanId,
        string plate,
        uint256 fine,
        string location
    );

    event ChallanPaid(uint256 challanId, address payer);

    event ChallanStatusUpdated(
        uint256 challanId,
        ChallanStatus status
    );

    constructor() {
        admin = msg.sender;
    }

    // ---------------------------------------------------
    // ADMIN FUNCTIONS
    // ---------------------------------------------------

    function addOfficer(address _officer) public onlyAdmin {
        officers[_officer] = true;
        emit OfficerAdded(_officer);
    }

    function addCamera(address _camera) public onlyAdmin {
        authorizedCameras[_camera] = true;
        emit CameraAuthorized(_camera);
    }

    function setFinePerKmhOver(uint256 _weiPerKmh)
        public
        onlyAdmin
    {
        finePerKmhOver = _weiPerKmh;
    }

    function registerVehicle(
        string memory _plate,
        address _owner
    ) public onlyAdmin {

        vehicles[_plate] = Vehicle({
            plateNumber: _plate,
            owner: _owner,
            exists: true
        });

        emit VehicleRegistered(_plate, _owner);
    }

    // ---------------------------------------------------
    // MANUAL CHALLAN
    // ---------------------------------------------------

    function issueChallan(
        string memory _plate,
        string memory _violationType,
        string memory _location,
        uint256 _fineAmount,
        string memory _evidenceHash,
        uint256 _violationTimestamp
    ) public onlyOfficer {

        require(
            vehicles[_plate].exists,
            "Vehicle not registered"
        );

        _createChallan(
            _plate,
            _violationType,
            _location,
            _fineAmount,
            _evidenceHash,
            _violationTimestamp,
            0,
            0
        );
    }

    // ---------------------------------------------------
    // CAMERA AUTOMATED CHALLAN
    // ---------------------------------------------------

    function issueChallanByCamera(
        string memory _plate,
        string memory _location,
        uint256 _detectedSpeed,
        uint256 _speedLimit,
        uint256 _violationTimestamp,
        string memory _evidenceHash
    ) public onlyCamera {

        require(
            vehicles[_plate].exists,
            "Vehicle not registered"
        );

        require(
            _detectedSpeed > _speedLimit,
            "Not overspeeding"
        );

        // ---------------------------------------------------
        // DUPLICATE PREVENTION
        // ---------------------------------------------------

        bytes32 violationHash = keccak256(
            abi.encodePacked(
                _plate,
                _location,
                _detectedSpeed,
                _speedLimit,
                _violationTimestamp,
                _evidenceHash
            )
        );

        require(
            !processedViolations[violationHash],
            "Duplicate violation"
        );

        processedViolations[violationHash] = true;

        uint256 overage = _detectedSpeed - _speedLimit;

        uint256 fine = overage * finePerKmhOver;

        _createChallan(
            _plate,
            "Overspeeding (automated)",
            _location,
            fine,
            _evidenceHash,
            _violationTimestamp,
            _detectedSpeed,
            _speedLimit
        );
    }

    // ---------------------------------------------------
    // INTERNAL CHALLAN CREATION
    // ---------------------------------------------------

    function _createChallan(
        string memory _plate,
        string memory _violationType,
        string memory _location,
        uint256 _fineAmount,
        string memory _evidenceHash,
        uint256 _violationTimestamp,
        uint256 _detectedSpeed,
        uint256 _speedLimit
    ) internal {

        challanCounter++;

        challans[challanCounter] = Challan({
            challanId: challanCounter,

            plateNumber: _plate,
            owner: vehicles[_plate].owner,

            violationType: _violationType,

            location: _location,

            fineAmount: _fineAmount,

            evidenceHash: _evidenceHash,

            violationTimestamp: _violationTimestamp,

            blockchainTimestamp: block.timestamp,

            status: ChallanStatus.Pending,

            detectedSpeed: _detectedSpeed,
            speedLimit: _speedLimit
        });

        emit ChallanIssued(
            challanCounter,
            _plate,
            _fineAmount,
            _location
        );
    }

    // ---------------------------------------------------
    // PAYMENT
    // ---------------------------------------------------

    function payChallan(uint256 _challanId)
        public
        payable
    {
        Challan storage c = challans[_challanId];

        require(
            c.status == ChallanStatus.Pending,
            "Challan not payable"
        );

        require(
            msg.sender == c.owner,
            "Not vehicle owner"
        );

        // Exact payment only
        require(
            msg.value == c.fineAmount,
            "Exact fine amount required"
        );

        c.status = ChallanStatus.Paid;

        (bool success, ) = payable(admin).call{
            value: msg.value
        }("");

        require(success, "Payment failed");

        emit ChallanPaid(_challanId, msg.sender);

        emit ChallanStatusUpdated(
            _challanId,
            ChallanStatus.Paid
        );
    }

    event PaymentRecorded(
    uint256 challanId,
    bytes32 paymentRef
);

function recordPayment(
    uint256 challanId,
    bytes32 paymentRef
)
    external
    onlyOfficer
{
    challans[challanId].status =
        ChallanStatus.Paid;

    emit PaymentRecorded(
        challanId,
        paymentRef
    );
}

    // -----------------------------+----------------------
    // ADMIN STATUS CONTROL
    // ---------------------------------------------------

    function updateChallanStatus(
        uint256 _challanId,
        ChallanStatus _status
    ) public onlyAdmin {

        challans[_challanId].status = _status;

        emit ChallanStatusUpdated(
            _challanId,
            _status
        );
    }

    // ---------------------------------------------------
    // VIEW FUNCTIONS
    // ---------------------------------------------------

    function getChallan(uint256 _id)
        public
        view
        returns (Challan memory)
    {
        return challans[_id];
    }

    function getVehicle(string memory _plate)
        public
        view
        returns (Vehicle memory)
    {
        return vehicles[_plate];
    }
}