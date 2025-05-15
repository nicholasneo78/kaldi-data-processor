# kaldi-data-processor
A simple repository to convert kaldi format manifest into a more readable format for data preprocessing

## About the Kaldi data format
For ASR task, the main files that would be required will likely be the following:
- `segments`
- `text`
- `wav.scp`

These three files are related to one another and are also related to the folder container the audio data, in terms of relative path. Hence, the filepath structure of these files have to be retained. You can find an example in the `data` directory. For this repository, we will rely heavily on the example data in kaldi format in the `data` directory.

**Structure of the Kaldi data in this repository**

```shell
data/
├── raw
│   ├── 1
│   │   ├── 1710986448546528638.wav
│   │   ├── 2
│   │   │   └── 3246112972111129481.wav
│   │   └── 2579704819843487674.wav
│   ├── 2
│   │   ├── 3
│   │   │   └── 8126899585335816719.wav
│   │   └── 6733125851564557061.wav
│   └── 843704469654597326.wav
├── segments
└── wav.scp
```

You can see the nested structure of the audio files being placed in this way intentionally.

### wav.scp
This file contains the **relative filepath** to the audio files with respect to where this `wav.scp` file is placed

Minimally it contains two parameters delimited by spacing

```shell
<audio_id> <relative_filepath>
```

`audio_id`: unique identifier for the audio file
`relative_filepath`: relative filepath of the audio from where the `wav.scp` file is placed


### segments
This file contains all the audio split in utterance form (because an audio defined in `wav.scp` file might contain more than 1 utterance, e.g an entry in `wav.scp` can have 4 utterances and hence 4 entries in the `segments` file)

Minimally it contains four parameters delimited by spacing

```shell
<audio_id_of_utterance> <audio_id> <start_ts> <end_ts>
```

`audio_id_of_utterance`: unique identifier for the particular utterance in the audio file
`audio_id`: unique identifier for the audio file (this will be use to match the `audio_id` in `wav.scp`)
`start_ts`: start time of the utterance in the audio file defined by the `audio_id`
`end_ts`: end time of the utterance in the audio file defined by the `audio_id`

### text
This file contains all the transcription of the audio utterance. Make sure the number of entries in this file is the same as the number of entries in that of `segments`

Minimally it contains two parameters delimited by spacing

```shell
<audio_id_of_utterance> <transcription>
```

`audio_id_of_utterance`: unique identifier for the particular utterance in the audio file
`transcription`: transcription of the utterance

### Combining together
Using the idea of **primary key** in database:
1. the parameters in `segments` will join with that of `text` with "primary key" `audio_id_of_utterance`
2. the combined `segments` and `text` implementation will then be joined with parameters from `wav.scp` with "primary key" `audio_id` 

The goal is to combine these three files to get a generic manifest that splits the audio in utterance form and a manifest ready for ASR training

Refer to `kaldi_to_nemo_manifest.py` and `nemo_to_hf_json_manifest.py` for the minimal implementation

## Setup
Before building the docker image, check the `build/docker-compose.yml` file and change the `volumes` of your dataset folders mounted accordingly 

Build the docker image

```shell
docker-compose -f build/docker-compose.yml build
```

Spin up a container from the built image (we will be running the processing code inside the container)

```shell
docker-compose -f build/docker-compose.yml run local bash
```

You should now be inside the container

## Running the script
Using the data examples in `data`, run the code:

```shell
python3 kaldi_to_nemo_manifest.py
```

You will expect a new directory `splits` be created with the split audio and the manifest file corresponding to the audio splits

You may continue to run `nemo_to_hf_json_manifest.py` to convert the manifest format into the huggingface json format

## Repeat with your own data
You can repeat the steps with your own data that resides in the mounted path in your `build/docker-compose.yml`