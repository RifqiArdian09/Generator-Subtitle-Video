import os
import json
import tempfile
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import moviepy.editor as mp
import whisper
import threading
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size (Vercel limit)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Using /tmp for Vercel serverless functions

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

class SubtitleGenerator:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.processing_status = {}
        
    def load_whisper_model(self):
        """Load Whisper model for better accuracy"""
        try:
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            return True
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")
            return False
    
    def extract_audio_from_video(self, video_path):
        """Extract audio from video file"""
        try:
            video = mp.VideoFileClip(video_path)
            audio_path = video_path.replace('.mp4', '_audio.wav').replace('.avi', '_audio.wav').replace('.mov', '_audio.wav')
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            raise Exception(f"Error extracting audio: {str(e)}")
    
    def generate_subtitles_whisper(self, audio_path, task_id):
        """Generate subtitles using Whisper for better accuracy"""
        try:
            self.processing_status[task_id] = {"status": "processing", "progress": 20}
            
            if not self.load_whisper_model():
                raise Exception("Failed to load Whisper model")
            
            self.processing_status[task_id] = {"status": "processing", "progress": 40}
            
            # Transcribe with timestamps
            result = self.whisper_model.transcribe(audio_path, word_timestamps=True)
            
            self.processing_status[task_id] = {"status": "processing", "progress": 70}
            
            subtitles = []
            for segment in result["segments"]:
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"].strip()
                
                if text:
                    subtitles.append({
                        "start": start_time,
                        "end": end_time,
                        "text": text
                    })
            
            self.processing_status[task_id] = {"status": "completed", "progress": 100}
            return subtitles
            
        except Exception as e:
            self.processing_status[task_id] = {"status": "error", "error": str(e)}
            raise Exception(f"Error generating subtitles: {str(e)}")
    
    def generate_subtitles_speech_recognition(self, audio_path, task_id):
        """Generate subtitles using speech recognition as fallback"""
        try:
            self.processing_status[task_id] = {"status": "processing", "progress": 20}
            
            # Load audio file
            audio = AudioSegment.from_wav(audio_path)
            
            # Split audio on silence
            chunks = split_on_silence(
                audio,
                min_silence_len=500,
                silence_thresh=audio.dBFS-14,
                keep_silence=500
            )
            
            self.processing_status[task_id] = {"status": "processing", "progress": 40}
            
            subtitles = []
            current_time = 0
            
            for i, chunk in enumerate(chunks):
                # Calculate timing
                chunk_duration = len(chunk) / 1000.0  # Convert to seconds
                start_time = current_time
                end_time = current_time + chunk_duration
                
                # Export chunk to temporary file
                chunk_filename = f"temp_chunk_{i}.wav"
                chunk.export(chunk_filename, format="wav")
                
                try:
                    # Recognize speech in chunk
                    with sr.AudioFile(chunk_filename) as source:
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio_data, language='id-ID')
                        
                        if text.strip():
                            subtitles.append({
                                "start": start_time,
                                "end": end_time,
                                "text": text.strip()
                            })
                
                except sr.UnknownValueError:
                    # Skip chunks that couldn't be recognized
                    pass
                except sr.RequestError as e:
                    print(f"Error with speech recognition service: {e}")
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(chunk_filename):
                        os.remove(chunk_filename)
                
                current_time = end_time
                
                # Update progress
                progress = 40 + (50 * (i + 1) / len(chunks))
                self.processing_status[task_id] = {"status": "processing", "progress": int(progress)}
            
            self.processing_status[task_id] = {"status": "completed", "progress": 100}
            return subtitles
            
        except Exception as e:
            self.processing_status[task_id] = {"status": "error", "error": str(e)}
            raise Exception(f"Error generating subtitles: {str(e)}")
    
    def format_time(self, seconds):
        """Format time in SRT format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def export_srt(self, subtitles, filename):
        """Export subtitles to SRT format"""
        srt_content = ""
        for i, subtitle in enumerate(subtitles, 1):
            start_time = self.format_time(subtitle["start"])
            end_time = self.format_time(subtitle["end"])
            text = subtitle["text"]
            
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        return filename
    
    def export_vtt(self, subtitles, filename):
        """Export subtitles to VTT format"""
        vtt_content = "WEBVTT\n\n"
        
        for subtitle in subtitles:
            start_time = self.format_time_vtt(subtitle["start"])
            end_time = self.format_time_vtt(subtitle["end"])
            text = subtitle["text"]
            
            vtt_content += f"{start_time} --> {end_time}\n{text}\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        
        return filename
    
    def format_time_vtt(self, seconds):
        """Format time in VTT format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"

# Initialize subtitle generator
subtitle_gen = SubtitleGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Generate task ID
        task_id = str(int(time.time() * 1000))
        
        # Start subtitle generation in background
        def generate_subtitles_async():
            try:
                # Extract audio
                subtitle_gen.processing_status[task_id] = {"status": "processing", "progress": 10}
                audio_path = subtitle_gen.extract_audio_from_video(filepath)
                
                # Try Whisper first, fallback to speech recognition
                try:
                    subtitles = subtitle_gen.generate_subtitles_whisper(audio_path, task_id)
                except:
                    print("Whisper failed, falling back to speech recognition")
                    subtitles = subtitle_gen.generate_subtitles_speech_recognition(audio_path, task_id)
                
                # Store results
                subtitle_gen.processing_status[task_id]["subtitles"] = subtitles
                
                # Clean up audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
            except Exception as e:
                subtitle_gen.processing_status[task_id] = {"status": "error", "error": str(e)}
        
        # Start background thread
        thread = threading.Thread(target=generate_subtitles_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'status': 'started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    status = subtitle_gen.processing_status.get(task_id, {"status": "not_found"})
    return jsonify(status)

@app.route('/export/<task_id>/<format>')
def export_subtitles(task_id, format):
    try:
        if task_id not in subtitle_gen.processing_status:
            return jsonify({'error': 'Task not found'}), 404
        
        status = subtitle_gen.processing_status[task_id]
        if status.get("status") != "completed" or "subtitles" not in status:
            return jsonify({'error': 'Subtitles not ready'}), 400
        
        subtitles = status["subtitles"]
        
        if format == 'srt':
            filename = f"subtitles_{task_id}.srt"
            filepath = os.path.join('static', filename)
            subtitle_gen.export_srt(subtitles, filepath)
        elif format == 'vtt':
            filename = f"subtitles_{task_id}.vtt"
            filepath = os.path.join('static', filename)
            subtitle_gen.export_vtt(subtitles, filepath)
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<task_id>')
def preview_subtitles(task_id):
    try:
        if task_id not in subtitle_gen.processing_status:
            return jsonify({'error': 'Task not found'}), 404
        
        status = subtitle_gen.processing_status[task_id]
        if status.get("status") != "completed" or "subtitles" not in status:
            return jsonify({'error': 'Subtitles not ready'}), 400
        
        return jsonify({'subtitles': status["subtitles"]})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Subtitle Generator Server...")
    print("Access the application at: http://localhost:5000")
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
