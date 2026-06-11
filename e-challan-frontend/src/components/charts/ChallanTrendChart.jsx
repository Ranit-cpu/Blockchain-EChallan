import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export function ChallanTrendChart({ data }) {
  return (
    <div className="h-[350px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <defs>
            <linearGradient id="challanGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#06b6d4" />
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
            contentStyle={{
              borderRadius: "12px",
              border: "none",
              background: "#111827",
              color: "#fff",
            }}
          />

          <Legend />

          <Bar
            dataKey="count"
            fill="url(#challanGradient)"
            radius={[10, 10, 0, 0]}
            barSize={34}
            animationDuration={1500}
            name="Challans"
          />

          <Line
            type="monotone"
            dataKey="count"
            stroke="#2563eb"
            strokeWidth={4}
            dot={{
              r: 5,
              fill: "#2563eb",
            }}
            activeDot={{
              r: 8,
            }}
            animationDuration={2000}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}