import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import type { SectionScore } from '../../types/evaluation';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BarChartProps {
  data: SectionScore[];
}

export function BarChartComponent({ data }: BarChartProps) {
  const chartData = {
    labels: data.map(d => d.section),
    datasets: [
      {
        label: 'Score',
        data: data.map(d => d.score),
        backgroundColor: 'rgba(99, 102, 241, 0.35)',
        borderColor: 'rgba(99, 102, 241, 0.85)',
        borderWidth: 1.5,
        borderRadius: 6,
        hoverBackgroundColor: 'rgba(99, 102, 241, 0.55)',
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 8,
        right: 8,
        top: 16,
        bottom: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 2,
          color: 'rgba(148, 163, 184, 0.9)',
          font: {
            size: 11,
          },
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.12)',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: 'rgba(226, 232, 240, 0.9)',
          font: {
            size: 11,
          },
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleColor: '#E2E8F0',
        bodyColor: '#F8FAFC',
        borderColor: 'rgba(71, 85, 105, 0.6)',
        borderWidth: 1,
        padding: 10,
        displayColors: false,
        callbacks: {
          label: (context) => {
            const value = typeof context.parsed.y === 'number' ? context.parsed.y : 0;
            return `Score: ${value.toFixed(1)}/10`;
          },
        },
      },
    },
  };

  return (
    <div className="h-[320px] w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}
