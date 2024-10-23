import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface PieChartProps {
  data: {
    [category: string]: number;
  };
  size?: number;
}

//  Generate a random color
const generateColor = () => {
    const getRandomColorComponent = () => Math.floor(Math.random() * 256);
    const r = getRandomColorComponent();
    const g = getRandomColorComponent();
    const b = getRandomColorComponent();
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  };
  
  // Generate an array of colors based on the number of categories
  const generateColorArray = (count: number) => {
    const colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(generateColor());
    }
    return colors;
  };
  
  const PieChart: React.FC<PieChartProps> = ({ data, size = 300 }) => {
    const labels = Object.keys(data);
    const values = Object.values(data);
    const colorArray = generateColorArray(labels.length);
  
    const chartData = {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: colorArray,
          hoverBackgroundColor: colorArray,
        },
      ],
    };
  
    const options = {
      responsive: true,
      maintainAspectRatio: true,
    };
  
    return (
      <div style={{ width: `${size}px`, height: `${size}px`, margin: '0 auto' }}>
        <Pie data={chartData} options={options} />
      </div>
    );
  };
  
  export default PieChart;