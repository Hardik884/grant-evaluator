import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import type { CritiqueDomain } from '../../types/evaluation';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface RadarChartProps {
  data: CritiqueDomain[];
}

export function RadarChartComponent({ data }: RadarChartProps) {
  const chartData = {
    labels: data.map(d => d.domain),
    datasets: [
      {
        label: 'Score',
        data: data.map(d => d.score),
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        borderColor: 'rgba(99, 102, 241, 0.8)',
        borderWidth: 1.5,
        pointBackgroundColor: 'rgba(236, 233, 252, 0.95)',
        pointBorderColor: 'rgba(99, 102, 241, 0.8)',
        pointHoverBackgroundColor: 'rgba(99, 102, 241, 1)',
        pointHoverBorderColor: '#F8FAFC',
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options: ChartOptions<'radar'> = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 10,
        angleLines: {
          color: 'rgba(148, 163, 184, 0.12)',
        },
        ticks: {
          stepSize: 2,
          color: 'rgba(148, 163, 184, 0.9)',
          backdropColor: 'transparent',
          showLabelBackdrop: false,
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.12)',
        },
        pointLabels: {
          color: 'rgba(226, 232, 240, 0.92)',
          font: {
            size: 12,
            weight: 500,
          },
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#1C2128',
        titleColor: '#F3F4F6',
        bodyColor: '#D1D5DB',
        borderColor: '#22272E',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: (context) => {
            const value = typeof context.parsed.r === 'number' ? context.parsed.r : 0;
            return `Score: ${value.toFixed(1)}/10`;
          },
        },
      },
    },
  };

  return (
    <div className="flex h-[320px] w-full items-center justify-center">
      <Radar data={chartData} options={options} />
    </div>
  );
}
