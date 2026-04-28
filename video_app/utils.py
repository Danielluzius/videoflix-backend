"""FFmpeg helpers: HLS conversion (480p/720p/1080p) and thumbnail extraction."""
import subprocess
import os


RESOLUTIONS = [
    {'name': '480p', 'scale': '854:480', 'bitrate': '800k', 'maxrate': '856k', 'bufsize': '1200k', 'audio': '96k'},
    {'name': '720p', 'scale': '1280:720', 'bitrate': '2800k', 'maxrate': '2996k', 'bufsize': '4200k', 'audio': '128k'},
    {'name': '1080p', 'scale': '1920:1080', 'bitrate': '5000k', 'maxrate': '5350k',
     'bufsize': '7500k', 'audio': '192k'},
]

BANDWIDTH_MAP = {'480p': 800000, '720p': 2800000, '1080p': 5000000}
RESOLUTION_MAP = {'480p': '854x480', '720p': '1280x720', '1080p': '1920x1080'}


def _build_ffmpeg_cmd(video_path, res, playlist_path, segment_pattern):
    """Return the FFmpeg command list for encoding a single HLS resolution variant."""
    video_opts = ['-c:v', 'libx264', '-crf', '20', '-sc_threshold', '0', '-g', '48', '-keyint_min', '48']
    bitrate_opts = ['-b:v', res['bitrate'], '-maxrate', res['maxrate'], '-bufsize', res['bufsize']]
    audio_opts = ['-c:a', 'aac', '-b:a', res['audio']]
    hls_opts = ['-hls_time', '6', '-hls_playlist_type', 'vod', '-hls_segment_filename', segment_pattern]
    return ['ffmpeg', '-y', '-i', video_path, '-vf', f"scale={res['scale']}",
            *video_opts, *bitrate_opts, *audio_opts, *hls_opts, playlist_path]


def _convert_resolution(video_path, output_dir, res):
    """Encode a single resolution variant and return (name, bitrate, playlist_path)."""
    res_dir = os.path.join(output_dir, res['name'])
    os.makedirs(res_dir, exist_ok=True)
    playlist_path = os.path.join(res_dir, 'index.m3u8')
    segment_pattern = os.path.join(res_dir, 'segment%03d.ts')
    cmd = _build_ffmpeg_cmd(video_path, res, playlist_path, segment_pattern)
    subprocess.run(cmd, check=True, capture_output=True)
    return res['name'], res['bitrate'], playlist_path


def _write_master_playlist(output_dir, variant_playlists):
    """Write master.m3u8 that references all resolution variants and return its path."""
    master_path = os.path.join(output_dir, 'master.m3u8')
    with open(master_path, 'w') as f:
        f.write('#EXTM3U\n')
        for name, _, _ in variant_playlists:
            bandwidth = BANDWIDTH_MAP[name]
            resolution = RESOLUTION_MAP[name]
            f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}\n')
            f.write(f'{name}/index.m3u8\n')
    return master_path


def convert_to_hls(video_path: str, output_dir: str) -> str:
    """Convert the source video to 480p/720p/1080p HLS variants and return the master playlist path."""
    os.makedirs(output_dir, exist_ok=True)
    variant_playlists = [_convert_resolution(video_path, output_dir, res) for res in RESOLUTIONS]
    return _write_master_playlist(output_dir, variant_playlists)


def generate_thumbnail(video_path: str, output_path: str) -> str:
    """Extract a single frame at the 3-second mark and save it as a 1280x720 JPEG."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-ss', '00:00:03', '-vframes', '1',
        '-vf', 'scale=1280:720',
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
