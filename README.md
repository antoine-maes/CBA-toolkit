This toolkit is still under development...


# CBA
The Conversation Behavior Analysis toolkit aims at offering the means for analyzing phenomena occurring in conversations such as mimicry, overlapping expressions, expressions timing, etc.


## Content

* /annotations: contains ELAN Template Files (etf) for annotation to use in your own projects.
* IBPY/extract_data.py : general functions to read/extract data.
* IBPY/db.py : interface specific to the different datasets.
* IBPY/interaction_analysis.py : functions for analysing interaction behaviors (ex. counting mimicry).
* IBPY/interaction_model.py : object oriented models of interactions.
* IBPY/visualization.py : visualization functions.
* IBPY/utils.py : utility functions.
* pair_data.py : example code


* [src]: This folder contains all functions we need to extract data from our dataset for the machine learning part and all extraction and vizualisation functions related to the statistics of smiles and laughs in our datasets. This also creates the custom json according to the contents of the data folder.

* [Streamlit]: This folder contains the needed files to display the SNL and ML statistics done in the corresponding folders in an interactive web page.

## How to run the code 

To launch Streamlit, run the following command from the terminal:
```python
python main.py 

```

## IMPORTANT

For the proper functioning of this toolbox, it is necessary to create a "data" folder containing your different datasets with annotated files in EAF format. This folder must be at the same level as the "src" or "Streamlit" folder, for example, at the root level.

For each new dataset different from ndc, ifadv or ccdb, you are asked to create in the "db.py" script:
* a function to return a list of files in pairs according to the way of naming them defined such as: form_pairs_foldername.
* a function to return the file paths of the pairs according to the way of naming them defined such as: form_list_pairs_nomdossier.

Rely on the already existing functions on this subject such as "form_pairs_ccdb" and "form_list_pairs_ccdb" for example

## Examples

To print corresponding pairs of interlocutors in the ccdb, ifadv or ndc datasets, run the following from the examples directory:

To print pairs from CCDB, IFADV or NDC-ME.
```python
python pair_data.py --path_ccdb <path to the CCDB audio, video or eaf files>
python pair_data.py --path_ifadv <path to the IFADV audio, video or eaf files>
python pair_data.py --path_ndc <path to the NDC-ME audio, video or eaf files>

```
