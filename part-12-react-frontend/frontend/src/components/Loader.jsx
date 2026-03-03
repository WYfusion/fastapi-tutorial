import React from 'react';

function Loader() {
  return (
    <div className='flex flex-col justify-center items-center h-screen w-screen bg-black text-white'>
      <div className='h-12 w-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin' />
      <p className='mt-4 text-sm text-gray-300'>Loading recipes...</p>
    </div>
  );
}

export default Loader;
