"""
Data preprocessing step to convert nemo format audio manifest to huggingface format
"""

from typing import Tuple, Dict, List
from tqdm import tqdm
import json
import os


class BuildHuggingFaceDataManifest:

    '''
    Generate updated manifest file, which is a format that huggingface can take in
    '''

    def __init__(
        self,
        input_manifest_path: str,
        output_manifest_path: str,
    ) -> None:

        '''
        input_manifest_path: manifest file path in nemo format
        output_manifest_path: manifest file path in huggingface format
        '''

        self.input_manifest_path = input_manifest_path
        self.output_manifest_path = output_manifest_path

    def load_manifest_nemo(self) -> List[Dict[str, str]]:

        '''
        loads the manifest file in Nvidia NeMo format to process the entries and store them into a list of dictionaries
        ---

        input_manifest_path: the manifest path that contains the information of the audio clips of interest
        ---
        returns: a list of dictionaries of the information in the input manifest file
        '''

        dict_list = []

        with open(self.input_manifest_path, 'r+') as f:
            for line in f:
                dict_list.append(json.loads(line))

        return dict_list

    def create_huggingface_manifest(self) -> List[Dict[str, str]]:

        '''
        loads the list of dictionaries of the data information, preprocess the manifest format and create the finalized list of dictionaries ready to export into a json file that is ready to be accepted by the huggingface datasets class
        ---

        input_manifest_path: the manifest path that contains the information of the audio clips of interest
        ---
        returns a list of dictionaries of the information in the huggingface format
        '''    

        dict_list = self.load_manifest_nemo()

        data_list = []

        for entries in tqdm(dict_list):

            data = {
                'file': f"{entries['audio_filepath']}",
                    'audio': {
                        'path': f"{entries['audio_filepath']}",
                        'sampling_rate': 16000
                    },
                    'text': entries['text'],
                    'duration': entries['duration']
            }

            data_list.append(data)

        return data_list

    
    def build_hf_data_manifest(self) -> Tuple[Dict[str, str], str]:

        '''
        main method to process the nemo format manifest file into the huggingface format manifest file
        '''

        # load all the data from the manifest
        data_list = self.create_huggingface_manifest()

        # form the final json manifest that is ready for export
        data_dict = {}
        data_dict['data'] = data_list

        # export to the final json format
        with open(f'{self.output_manifest_path}', 'w', encoding='utf-8') as f:
            f.write(json.dumps(data_dict, indent=2, ensure_ascii=False))

        # returns the final preprocessed dataframe and the filepath of the json file
        return data_dict, self.output_manifest_path
    

    def __call__(self):
        return self.build_hf_data_manifest()
    
if __name__ == '__main__':

    ROOT_DIR = '/kaldi_data_processor/data'
    INPUT_MANIFEST_DIR = os.path.join(ROOT_DIR, "manifest_nemo.json")
    OUTPUT_MANIFEST_DIR = os.path.join(ROOT_DIR, "manifest_hf.json")

    b = BuildHuggingFaceDataManifest(
        input_manifest_path=INPUT_MANIFEST_DIR,
        output_manifest_path=OUTPUT_MANIFEST_DIR,
    )()