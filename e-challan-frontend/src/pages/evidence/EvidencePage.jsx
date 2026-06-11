import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Loader2 } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { FileUpload } from '@/components/common/FileUpload';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { evidenceApi } from '@/api';
import { useToast } from '@/hooks/useToast';
import { formatDate } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { challansApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';

export default function EvidencePage() {
  const [files, setFiles] = useState([]);
  const [challanId, setChallanId] = useState('');
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['evidence-list'],
    queryFn: async () => {
      const { data: res } = await evidenceApi.list({ page: 1, page_size: 20 });
      return res;
    },
  });


  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!challanId) throw new Error('Enter challan ID');
      const formData = new FormData();
      formData.append('file', files[0]);
      if (description) formData.append('description', description);
      return challansApi.uploadEvidence(challanId, formData, setProgress);
    },
    onSuccess: (res) => {
      toast({ title: 'Evidence uploaded', description: unwrapData(res)?.message });
      setFiles([]);
      setChallanId('');
      setProgress(0);
    },
    onError: (err) => toast({ title: 'Upload failed', description: err.message, variant: 'destructive' }),
  });

  const items = data?.items || data || [];

  return (
    <div className="space-y-6">
      <PageHeader title="Evidence Upload" description="Upload violation evidence for challans" />
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload New Evidence
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2 max-w-sm">
            <Label htmlFor="challan_id">Challan ID</Label>
            <Input
              id="challan_id"
              placeholder="Enter challan UUID"
              value={challanId}
              onChange={(e) => setChallanId(e.target.value)}
            />
          </div>
          <FileUpload onFilesSelected={setFiles} multiple />
          {progress > 0 && progress < 100 && (
            <div className="w-full bg-muted rounded-full h-2">
              <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
            </div>
          )}
          <Button
            onClick={() => uploadMutation.mutate()}
            disabled={!challanId || files.length === 0 || uploadMutation.isPending}
          >
            {uploadMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Upload Evidence
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Recent Uploads</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File</TableHead>
                  <TableHead>Challan</TableHead>
                  <TableHead>Uploaded</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell>
                      <a href={e.file_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                        {e.file_name}
                      </a>
                    </TableCell>
                    <TableCell>{e.challan_number || e.challan_id}</TableCell>
                    <TableCell>{formatDate(e.created_at, { time: true })}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
