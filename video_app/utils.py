import subprocess
import os
from pathlib import Path


def convert_to_hls(video_path: str, output_dir: str) -> str:
    """
    Converts a video file to HLS format with 3 quality levels (480p, 720p, 1080p).
    Returns the path to the master playlist (.m3u8).
    """
    os.makedirs(output_dir, exist_ok=True)

    resolutions = [
        {'name': '480p', 'scale': '854:480', 'bitrate': '800k', 'maxrate': '856k', 'bufsize': '1200k', 'audio': '96k'},
        {'name': '720p', 'scale': '1280:720', 'bitrate': '2800k', 'maxrate': '2996k', 'bufsize': '4200k', 'audio': '128k'},
        {'name': '1080p', 'scale': '1920:1080', 'bitrate': '5000k', 'maxrate': '5350k', 'bufsize': '7500k', 'audio': '192k'},
    ]

    variant_playlists = []

    for res in resolutions:
        res_dir = os.path.join(output_dir, res['name'])
        os.makedirs(res_dir, exist_ok=True)
        playlist_path = os.path.join(res_dir, 'index.m3u8')
        segment_pattern = os.path.join(res_dir, 'segment%03d.ts')

        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"scale={res['scale']}",
            '-c:v', 'libx264', '-crf', '20', '-sc_threshold', '0',
            '-g', '48', '-keyint_min', '48',
            '-b:v', res['bitrate'], '-maxrate', res['maxrate'], '-bufsize', res['bufsize'],
            '-c:a', 'aac', '-b:a', res['audio'],
            '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            playlist_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        variant_playlists.append((res['name'], res['bitrate'], playlist_path))

    # Master playlist
    master_path = os.path.join(output_dir, 'master.m3u8')
    bandwidth_map = {'480p': 800000, '720p': 2800000, '1080p': 5000000}
    resolution_map = {'480p': '854x480', '720p': '1280x720', '1080p': '1920x1080'}

    with open(master_path, 'w') as f:
        f.write('#EXTM3U\n')
        for name, _, playlist_path in variant_playlists:
            rel_path = f"{name}/index.m3u8"
            f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth_map[name]},RESOLUTION={resolution_map[name]}\n')
            f.write(f'{rel_path}\n')

    return master_path


def generate_thumbnail(video_path: str, output_path: str) -> str:
    """
    Extracts a thumbnail from the video at the 3-second mark.
    Returns the path to the thumbnail.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-ss', '00:00:03', '-vframes', '1',
        '-vf', 'scale=1280:720',
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
