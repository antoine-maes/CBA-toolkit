This toolkit is still under development...


# CBA
The Conversation Behavior Analysis toolkit aims at offering the means for analyzing phenomena occurring in conversations such as mimicry, overlapping expressions, expressions timing, etc.


## Content

* [annotations]: contains ELAN Template Files (etf) for annotation to use in your own projects.
* [data]: contains the data used for the statistics and machine learning parts of the project. This folder is not included in the repository, it will be created thanks to the MainPage of the Streamlit interface with your database of choice.
* [src]: contains all functions we need to process data from our datasets for the machine learning part and all extraction and vizualisation functions related to the statistics of expressions in our datasets. This also creates the custom json according to the contents of the data folder.
* [Dash]: contains the needed files to display the Non Verbal Expressions and ML statistics done in the corresponding folders in an interactive web page.
* pair_data.py : example code

## How to run the code 

To launch Dash, run the following command from the terminal:
```python
cd Dash
python app.py
```

### IMPORTANT POUR SARRA

aller sur ma branche de CBA 
```bash 
git checkout rebuild-dash
```

Mise à jour du submodule IBPY
```bash 
Git submodule sync
```

Aller dans IBPY
```bash 
Cd IBPY
```

Récupérer toutes les branches de IBPY (sur mon fork de IBPY)
```bash 
git fetch origin
```

Aller sur la branche CBA-Dash
```bash 
git checkout CBA-Dash
```

## IMPORTANT

For the proper functioning of this toolbox, it is necessary to implement your different datasets with annotated files in EAF format under the same template. You will be asked to provide them to the interface in zip format, one folder at a time.

If your eaf files do not follow the naming convention "A_number_..." & "B_number_..." for each interaction, you are asked to create in the "db.py" script or in the MainPage:
* a function to return a list of files in pairs according to the way of naming them defined such as: form_pairs_foldername.

Rely on the already existing functions on this subject such as "form_pairs_ab".

## Examples

To print corresponding pairs of interlocutors in the ccdb, ifadv or ndc datasets, run the following from the examples directory:

To print pairs from CCDB, IFADV or NDC-ME.
```python
python pair_data.py --path_ccdb <path to the CCDB audio, video or eaf files>
python pair_data.py --path_ifadv <path to the IFADV audio, video or eaf files>
python pair_data.py --path_ndc <path to the NDC-ME audio, video or eaf files>

```
## Installation

To install the toolkit, clone the repository and install : 

First of all, you need to clone the repository on github (https://github.com/kelhad00/CBA-toolkit/tree/dev) or download it.

After that, you need to create a virtual environment to use web interface (Streamlit) :

    Step 1 : Install Environment creation Tool (Anaconda or Miniconda for examples).
    Step 2 : Launch Visual Studio Code from your tool.
    Step 3 : Open project folder.
    Step 4 : Install dependencies (libraries). All dependencies are on requirements.txt
                - To install dependencies you need to open terminal on Visual Studio Code and write ``` pip install -r requirements.txt ``` 

That's it, your project is set up to start !