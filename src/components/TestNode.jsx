import React from 'react';
import { Handle, Position } from '@xyflow/react';

const TestNode = ({ data, isConnectable }) => {
  return (
    <div className="bg-red-500 text-white p-4 rounded-lg shadow-lg w-48 h-32 flex items-center justify-center">
      <div className="text-center">
        <div className="text-lg font-bold">Test Node</div>
        <div className="text-sm">ID: {data?.id || 'unknown'}</div>
      </div>
      
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-white border-2 border-red-500"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-white border-2 border-red-500"
      />
    </div>
  );
};

export default TestNode;
