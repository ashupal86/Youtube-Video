from flask import Flask, render_template, request, jsonify,send_file
from pytube import YouTube
import os
import re

def sanitize_filename(filename):
    # Remove invalid characters from the filename
    return re.sub(r'[^\w\-_.() ]', '_', filename)

app = Flask(__name__)

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/get_video',methods=['GET'])
def get_video():
    
    try:
        url=request.args.get('url')
        if not url:
            return jsonify({'error':'No url provided'}),400
        print(url)
        yt=YouTube(url)
        print('Gathering info...')
        title=yt.title
        video=yt.streams.filter(only_video=True,file_extension='mp4')
        audio=yt.streams.filter(only_audio=True,file_extension='mp4')
        # print(video,audio,title)
        video_list = [{'resolution': stream.resolution, 'mime_type': stream.mime_type, 'itag': stream.itag} for stream in video]
        audio_list = [{'abr': stream.abr, 'mime_type': stream.mime_type, 'itag': stream.itag} for stream in audio]
        
        data= {'title':title,'video':video_list,'audio':audio_list}
        return render_template('download.html',data=data,url=url),200
    except Exception as e:
        return jsonify({'error':str(e)}),400

@app.route('/download',methods=['GET'])
def download():
    try:
        url=request.args.get('url')
        video=request.args.get('video')
        audio=request.args.get('audio')
        print(url,video,audio)
        Type=request.args.get('type')
        if not url:
            return jsonify({'error':'No url provided'}),400
        
        if Type=='video':
            itag=video
        else:
            itag=audio
        yt=YouTube(url)
        print('Gathering info...')
        title=yt.title
        filename=sanitize_filename(title)
        stream=yt.streams.get_by_itag(itag)
        downloads_dir = os.path.join(app.root_path, 'static', 'downloads')
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)

        file_path = os.path.join(downloads_dir, f'{filename}.mp4')
        stream.download(output_path=downloads_dir,filename=f'{filename}.mp4')


        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True,download_name=f'{filename}.mp4'),200
    except Exception as e:
        
        return jsonify({'error':str(e)}),400  

if __name__ == '__main__':
    app.run(debug=True,port=8000,host='0.0.0.0')