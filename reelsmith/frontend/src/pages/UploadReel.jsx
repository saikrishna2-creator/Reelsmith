import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const UploadReel = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [musicFile, setMusicFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [finalVideoUrl, setFinalVideoUrl] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!jobId) return;

    const pollStatus = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/getStatus/${jobId}`);
        const { status: jobStatus, finalVideoUrl: url, error: jobError } = response.data;

        setStatus(`Job status: ${jobStatus}`);
        if (jobStatus === 'processing') {
          setProgress((prev) => (prev < 90 ? prev + 10 : 90));
        } else if (jobStatus === 'completed') {
          setProgress(100);
          setFinalVideoUrl(url);
          setJobId(null);
          clearInterval(pollStatus);
        } else if (jobStatus === 'failed') {
          setError(`Processing failed: ${jobError}`);
          setJobId(null);
          clearInterval(pollStatus);
        }
      } catch (err) {
        setError('Error polling for status.');
        console.error(err);
        clearInterval(pollStatus);
      }
    }, 3000);

    return () => clearInterval(pollStatus);
  }, [jobId]);

  const handleProcessReel = async () => {
    if (!videoFile || !musicFile) {
      setError('Please select both a video and a music file.');
      return;
    }
    setError('');
    setStatus('Uploading files...');
    setProgress(10);

    const formData = new FormData();
    formData.append('videoFile', videoFile);
    formData.append('musicFile', musicFile);

    try {
      // 1. Upload files
      const uploadResponse = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { videoUrl, musicUrl } = uploadResponse.data;

      setStatus('Files uploaded. Starting processing...');
      setProgress(30);

      // 2. Process reel
      const processResponse = await axios.post(`${API_BASE_URL}/processReel`, {
        videoUrls: [videoUrl],
        musicUrl: musicUrl,
        niche: "travel", // Niche is hardcoded for now
      });
      setJobId(processResponse.data.jobId);
      setStatus('Processing started. Waiting for status updates...');
      setProgress(50);

    } catch (err) {
      setError('An error occurred during the process.');
      console.error(err);
      setStatus('');
      setProgress(0);
    }
  };

  return (
    <div className="container mx-auto max-w-2xl p-8 bg-gray-800 rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-6 text-center text-white">Create Your Reel</h1>

      <div className="space-y-6">
        <div>
          <Label htmlFor="video-file" className="text-lg text-gray-300">Video File</Label>
          <Input
            id="video-file"
            type="file"
            onChange={(e) => setVideoFile(e.target.files[0])}
            className="mt-2 bg-gray-700 text-white border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <Label htmlFor="music-file" className="text-lg text-gray-300">Background Music</Label>
          <Input
            id="music-file"
            type="file"
            onChange={(e) => setMusicFile(e.target.files[0])}
            className="mt-2 bg-gray-700 text-white border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <Button
          onClick={handleProcessReel}
          disabled={!videoFile || !musicFile || !!jobId}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 text-lg"
        >
          {jobId ? 'Processing...' : 'Process Reel'}
        </Button>
      </div>

      {status && (
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4 text-center">Processing Status</h2>
          <Progress value={progress} className="w-full bg-gray-700" />
          <p className="text-center mt-4 text-gray-400">{status}</p>
        </div>
      )}

      {error && <p className="text-red-500 text-center mt-4">{error}</p>}

      {finalVideoUrl && (
        <div className="mt-8 text-center">
          <h2 className="text-2xl font-semibold mb-4">Reel Ready!</h2>
          <video controls src={finalVideoUrl} className="w-full rounded-lg"></video>
          <a
            href={finalVideoUrl}
            download="final_reel.mp4"
            className="mt-4 inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            Download Reel
          </a>
        </div>
      )}
    </div>
  );
};

export default UploadReel;
