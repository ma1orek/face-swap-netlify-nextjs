import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import ffmpeg from 'fluent-ffmpeg';
import ffmpegPath from 'ffmpeg-static';

ffmpeg.setFfmpegPath(ffmpegPath);
export const config = { api: { bodyParser: false } };

export default async function handler(req, res) {
  const form = new formidable.IncomingForm({ keepExtensions: true });
  form.parse(req, async (err, fields, files) => {
    if (err) return res.status(500).send(err.message);
    const videoPath = files.video.filepath;
    const facePath = files.image.filepath;
    const tmpDir = path.dirname(videoPath);
    const gifPath = path.join(tmpDir, 'input.gif');
    const audioPath = path.join(tmpDir, 'audio.aac');
    const swappedGifPath = path.join(tmpDir, 'swapped.gif');
    const outputPath = path.join(tmpDir, 'output.mp4');

    try {
      await new Promise((r, e) => {
        ffmpeg(videoPath)
          .outputOptions('-vf', 'fps=25,scale=320:-1')
          .save(gifPath)
          .on('end', r).on('error', e);
      });
      await new Promise((r, e) => {
        ffmpeg(videoPath)
          .noVideo()
          .save(audioPath)
          .on('end', r).on('error', e);
      });
      const formData = new FormData();
      formData.append('source', fs.createReadStream(gifPath));
      formData.append('face', fs.createReadStream(facePath));
      formData.append('mode', 'easel-gifswap');
      const falRes = await fetch('https://api.fal.ai/v1/image/transform', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${process.env.FAL_AI_KEY}` },
        body: formData
      });
      const swapBuffer = await falRes.buffer();
      fs.writeFileSync(swappedGifPath, swapBuffer);
      await new Promise((r, e) => {
        ffmpeg()
          .addInput(swappedGifPath)
          .addInput(audioPath)
          .outputOptions('-c:v libx264', '-c:a aac', '-shortest')
          .save(outputPath)
          .on('end', r).on('error', e);
      });
      const stat = fs.statSync(outputPath);
      res.writeHead(200, {
        'Content-Type': 'video/mp4',
        'Content-Length': stat.size
      });
      fs.createReadStream(outputPath).pipe(res);
    } catch (e) {
      console.error(e);
      res.status(500).send('Processing error');
    }
  });
}
