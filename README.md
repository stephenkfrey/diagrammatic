# Diagrammatic

The main function is in `image_extraction_pipeline.py`

It accepts: 

1) a single filepath or a directory

2) (optional) `--output-dir` the output directory to save it to 

3) (optional) `--max-workers`  max workers to use when parallel processing a directory of files

``````
python image_extraction_pipeline.py sample_data/dl15.pdf

python image_extraction_pipeline.py sample_data/DL_textbooks/ --output-dir myoutput --max-workers 4

``````

