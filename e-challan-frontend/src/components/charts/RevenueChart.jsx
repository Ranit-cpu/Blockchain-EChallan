import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export function RevenueChart({ data }) {
  return (
    <div className="h-[350px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.15}
          />

          <XAxis
            dataKey="month"
            tickLine={false}
            axisLine={false}
          />

          <YAxis
            tickLine={false}
            axisLine={false}
          />

          <Tooltip
            formatter={(value) =>
              `₹${Number(value).toLocaleString()}`
            }
            contentStyle={{
              borderRadius: "12px",
              border: "none",
              background: "#111827",
              color: "#fff",
            }}
          />

          <Legend />

          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#10b981"
            fillOpacity={1}
            fill="url(#revenueGradient)"
            strokeWidth={4}
            animationDuration={2000}
            name="Revenue"
          />

          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#059669"
            strokeWidth={3}
            dot={{
              r: 4,
              fill: "#059669",
            }}
            activeDot={{
              r: 7,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}