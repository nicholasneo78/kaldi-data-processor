"""
To convert the kaldi format data (requires the wav.scp, segments and text files only) to produce a basic ASR manifest in the nemo format which looks like this:

manifest.json
-------------

{"audio_filepath": "relative/path/to/audio1.wav", "duration": <duration_in_sec>, "text": "transcription 1"}
{"audio_filepath": "relative/path/to/audio2.wav", "duration": <duration_in_sec>, "text": "transcription 2"}
{"audio_filepath": "relative/path/to/audio3.wav", "duration": <duration_in_sec>, "text": "transcription 3"}
...
...

"""

import os
import json
import subprocess
from typing import Dict
from tqdm import tqdm
import pandas as pd

class KaldiToNemoManifest:

    """
    main class to convert the kaldi format to nemo manifest
    """

    def __init__(
        self,
        root_dir: str,
        kaldi_config_dir: Dict[str, str],
        output_audio_subdir: str,
        output_manifest_dir: str,
    ) -> None:
        
        self.root_dir = root_dir
        self.kaldi_config_dir = kaldi_config_dir
        self.output_audio_subdir = output_audio_subdir
        self.output_manifest_dir = output_manifest_dir

    def split_audio_based_on_timing(self, main_filename: str, split_filename: str, start: str, end: str) -> None:

        """
        sox implementation of splitting the long audio file into utterance level
        ---
        main_filename: raw audio filepath
        split_filename: split audio filepath
        start: start timestamp in string
        end: end timestamp in string
        """

        subprocess.run(['sox', main_filename, split_filename, 'trim', start, str(float(end)-float(start))])

    def convert(self) -> None:

        with open(self.kaldi_config_dir['wav.scp'], 'r+') as fr:
            wav_scp_data = [entry.replace('\n', '').split(" ") for entry in fr.readlines()]

        with open(self.kaldi_config_dir['segments'], 'r+') as fr:
            segments_data = [entry.replace('\n', '').split(" ") for entry in fr.readlines()]

        with open(self.kaldi_config_dir['text'], 'r+') as fr:
            text_data = [entry.replace('\n', '').split(" ", 1) for entry in fr.readlines()]

        if len(segments_data) != len(text_data):
            assert ValueError("Number of segments should correspond to the number of text entries!")

        wav_scp_df = pd.DataFrame(wav_scp_data, columns=["index", "path"])
        segments_df = pd.DataFrame(segments_data, columns=["index_seg", "index", "seg_start", "seg_end"])
        text_df = pd.DataFrame(text_data, columns=["index_seg", "text"])

        # merge the dataframes
        seg_and_text_df = segments_df.merge(text_df, how="left", on="index_seg")
        combined_df = wav_scp_df.merge(seg_and_text_df, how="left", on="index")

        output_manifest_list = []
        
        for idx, row in tqdm(combined_df.iterrows()):
            input_audio_path = os.path.join(self.root_dir, row['path'])

            # e.g /kaldi_data_processor/data/raw/2/3/8126899585335816719.wav  --> /kaldi_data_processor/data/splits/2/3/8126899585335816719_split_0.wav
            output_audio_path = os.path.join(
                os.path.dirname(
                    os.path.join(
                        self.output_audio_subdir,
                        row['path'].split('/', 1)[-1] # to remove the subfolder
                    )
                ),
                f"{row['index_seg']}.wav"
            )

            os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
            self.split_audio_based_on_timing(
                main_filename=input_audio_path,
                split_filename=output_audio_path,
                start=row['seg_start'],
                end=row['seg_end']
            )

            output_manifest_entry = {
                "audio_filepath": output_audio_path.replace(self.root_dir+'/', ""),
                "raw_audio_filepath": row['path'],
                "duration": round(float(row['seg_end']) - float(row['seg_start']), 5),
                "text": row['text']
            }

            output_manifest_list.append(output_manifest_entry)

        with open(self.output_manifest_dir, 'w+', encoding='utf-8') as f:
            for data in output_manifest_list:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')


    def __call__(self) -> None:

        return self.convert()
    
if __name__ == '__main__':

    ROOT_DIR = '/kaldi_data_processor/data'
    KALDI_CFG = {
        'wav.scp': os.path.join(ROOT_DIR, 'wav.scp'),
        'segments': os.path.join(ROOT_DIR, 'segments'),
        'text': os.path.join(ROOT_DIR, 'text'),
    }
    OUTPUT_SUBDIR = 'splits'
    OUTPUT_AUDIO_SUBDIR = os.path.join(ROOT_DIR, OUTPUT_SUBDIR)
    OUTPUT_MANIFEST_DIR = os.path.join(ROOT_DIR, 'manifest_nemo.json')

    k = KaldiToNemoManifest(
        root_dir=ROOT_DIR,
        kaldi_config_dir=KALDI_CFG,
        output_audio_subdir=OUTPUT_AUDIO_SUBDIR,
        output_manifest_dir=OUTPUT_MANIFEST_DIR
    )()

