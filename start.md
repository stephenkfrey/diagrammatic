# Envision 

Goal: For any technical / scientific concept, immediately see the best visual explanations of it that have ever been created 

Make a dataset and API 

Use for generating books, study guides or videos 

## 1. Build a massive dataset of technical diagerams 

- load PDFs (textbooks) into diagram extraction pipeline
    - extract all Diagrams + Figures via (via an image extraction API ie unstructured.io)
    - extract the captions (and references within the text) for each Figure 
    - we could start with open-source Machine Learning Textbooks https://drive.google.com/drive/folders/1xUAKnJ7U0Yz_0G8bhkxurWhE_OmaA67S
    - Here is the master folder of textboooks: https://drive.google.com/drive/u/1/folders/1XpvH5SvwY1BUruGkxZ8EpeekmzhYZhvt 

## 2. Post it on HuggingFace

## 3.  Build a Diagram Retrieval API 

- Given any technical/scientific concept, retrieve the top (diagram, caption) pairs to explain it 


## 4. Bonus: Could we build a Diagram Generation model? 

- great if you've worked on creating reliable text in image generation models 