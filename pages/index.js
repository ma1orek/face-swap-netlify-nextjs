import { useState } from 'react';

export default function Home() {
  const [video, setVideo] = useState(null);
  const [image, setImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [outputUrl, setOutputUrl] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    const form = new FormData();
    form.append('video', video);
    form.append('image', image);
    setProcessing(true);
    const res = await fetch('/api/process', { method: 'POST', body: form });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    setOutputUrl(url);
    setProcessing(false);
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">Face-Swap Video Processor</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label>Video File:</label>
          <input type="file" accept="video/*" onChange={e => setVideo(e.target.files[0])} required />
        </div>
        <div>
          <label>Face Image:</label>
          <input type="file" accept="image/*" onChange={e => setImage(e.target.files[0])} required />
        </div>
        <button type="submit" disabled={processing} className="px-4 py-2 bg-blue-600 text-white rounded">
          {processing ? 'Processing...' : 'Start'}
        </button>
      </form>
      {outputUrl && (
        <div className="mt-6">
          <h2 className="text-xl">Result:</h2>
          <video src={outputUrl} controls className="mt-2 max-w-full" />
        </div>
      )}
    </div>
  );
}
