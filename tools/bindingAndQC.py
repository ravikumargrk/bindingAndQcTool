import pandas as pd
import numpy as np

from importlib.resources import read_binary
core_unserialized = read_binary(__package__, 'standardMetaMatrix.bin')

import dill
standardMetaMatrix = dill.loads(core_unserialized)

META_END_COLUMN_INDEX = 25
MATRIX_START_COLUMN_INDEX = 27
# standardMetaMatrix = pd.DataFrame.from_dict(standardMetaMatrixDict)

# load config
config = {
    'super heater exists'           : True,
    'Boiler type [RG=1, FBC=2]'     : 1,
    'fuel totaliser unit'           :'KG',
    'steam totaliser unit'          :'KG',
    'water totaliser unit'          :'KG',
    'load brackets'                 : 5,
    'Number of grates/beds'         : 2
}

maskForMultipleComponents = (standardMetaMatrix[('-', '-', '-', '-','componentInstance')] == '__c__') #| (standardMetaMatrix[('-', '-', '-', '-','subcomponentInstance')] == '__c__')
maskForMultipleSubComponents = standardMetaMatrix[('-', '-', '-', '-','subcomponentInstance')] == '__s__'

repeatingComponents = set(standardMetaMatrix[maskForMultipleComponents][('-', '-', '-', '-','component')])

# adding repeating components
for item in repeatingComponents:
    config.update({item:{'instances':1}})

repeatingSubComponentsDF = standardMetaMatrix[maskForMultipleSubComponents][[('-', '-', '-', '-','component'), ('-', '-', '-', '-', 'subcomponent')]]
repeatingSubComponents = set(repeatingSubComponentsDF.itertuples(index=False, name=None))

# adding repeating sub-components
for item in repeatingSubComponents:
    if item[0] in config:
        config[item[0]].update({item[1]:{'instances': 1}})
    else:
        config.update({item[0]:{item[1]:{'instances': 1}}})

def multiply(metaMatrix, description:str, replaceStr:str, instances):
    
    mask = metaMatrix[metaMatrix.columns[0]] == description
    row = metaMatrix[mask]
    metaMatrix = metaMatrix[~(mask)]
    
    if len(row.index) > 0:
        for instance in range(1, instances+1):
            newRowDict = {}
            rowDict = dict(row)

            for key in rowDict:
                if type(rowDict[key][row.index[0]])==str:
                    newRowDict.update(
                        {
                            key : [rowDict[key][row.index[0]].replace(replaceStr,str(instance))]
                        }
                    )
                else:
                    newRowDict.update(
                        {
                            key : [rowDict[key][row.index[0]]]
                        }
                    )
            metaMatrix = metaMatrix.append(pd.DataFrame.from_dict(newRowDict), ignore_index=True)

    return metaMatrix

def generateTemplate(config:dict, CSVfileName='bindingSheet'):
    ###########################################################################
    # tag Matrix and unit configuration
    replaceDict = {
        '__total_fuel_unit__'  : config['fuel totaliser unit'],
        '__total_steam_unit__' : config['steam totaliser unit'],
        '__total_water_unit__' : config['water totaliser unit'],
        '__super__'            : int(config['super heater exists'])
    }

    if config['Boiler type [RG=1, FBC=2]'] in [1]:
        #if RG boiler
        replaceDict.update(
            {
                '__grate__'     : 1,
                '__bed__'       : 0,
                '__system__'    : 'RG Boiler',
                '__systemName__': 'RG 1'
            }
        )
    if config['Boiler type [RG=1, FBC=2]'] in [2]:
        replaceDict.update(
            {
                '__grate__'     : 0,
                '__bed__'       : 1,
                '__system__'    : 'CFBC Boiler',
                '__systemName__': 'FBC 1'
            }
        )

    metaMatrix = standardMetaMatrix.replace(replaceDict)

    ###########################################################################
    # meta-tree configuration
    # numberOfPrimaryFDFans = config['equipmentConfig']['number of (primary) FD fans']
    # metaMatrix = multiply(metaMatrix, 'PRIMARY FD FAN NO.X START/STOP', 'X', numberOfPrimaryFDFans)

    # # 'number of trolleys in each grate'
    # numberOfTrolleys = config['equipmentConfig']['number of trolleys in each grate']
    # metaMatrix = multiply(metaMatrix, 'GRATE TROLLEY NO.X FORWARD SOV ON/OFF', 'X', numberOfTrolleys)
    # metaMatrix = multiply(metaMatrix, 'GRATE TROLLEY NO.X REVERSE SOV ON/OFF', 'X', numberOfTrolleys)
    
    # Number of grates/beds
    maskForMultipleGrates = metaMatrix[('-', '-', '-', '-','systemInstance')] == '__z__'
    for row in metaMatrix[maskForMultipleGrates].iterrows():
        desc = row[1][('-', '-', '-', '-', 'description')]
        metaMatrix = multiply(metaMatrix, desc, '__z__', config['Number of grates/beds'])

    maskForMultipleComponents = (metaMatrix[('-', '-', '-', '-','componentInstance')] == '__c__') #| (metaMatrix[('-', '-', '-', '-','subcomponentInstance')] == '__c__')
    for row in metaMatrix[maskForMultipleComponents].iterrows():
        desc = row[1][('-', '-', '-', '-', 'description')]
        comp = row[1][('-', '-', '-', '-', 'component')]
        instances = config[comp]['instances']
        # if row[1][('-', '-', '-', '-','subcomponentInstance')] == '__c__':
        #     subcomp = row[1][('-', '-', '-', '-', 'subcomponent')]
        #     instances = config[comp][subcomp]['instances']
        metaMatrix = multiply(metaMatrix, desc, '__c__', instances)
        
    maskForMultipleSubComponents = metaMatrix[('-', '-', '-', '-','subcomponentInstance')] == '__s__'
    for row in metaMatrix[maskForMultipleSubComponents].iterrows():
        desc = row[1][('-', '-', '-', '-', 'description')]
        comp = row[1][('-', '-', '-', '-', 'component')]
        subcomp = row[1][('-', '-', '-', '-', 'subcomponent')]
        instances = config[comp][subcomp]['instances']
        metaMatrix = multiply(metaMatrix, desc, '__s__', instances)

    maskForMultipleLoadBuckets = metaMatrix[('-', '-', '-', '-','measureInstance')] == '__m__'
    for row in metaMatrix[maskForMultipleLoadBuckets].iterrows():
        desc = row[1][('-', '-', '-', '-', 'description')]
        metaMatrix = multiply(metaMatrix, desc, '__m__', config['load brackets'])

    # remove unwanted rows
    maskForUnwanted = metaMatrix[('-', '-', '-', '-','includeInBindingUI')] == 0
    for row in metaMatrix[maskForUnwanted].iterrows():
        desc = row[1][('-', '-', '-', '-', 'description')]
        metaMatrix = multiply(metaMatrix, desc, '__dummy__', 0)
        
    ###########################################################################
    # exporting files
    bindingToolStandardDescriptions = metaMatrix[metaMatrix.columns[0]]

    bindingSheet = pd.DataFrame.from_dict(
        {
            'dataTagId'  : ['' for x in list(bindingToolStandardDescriptions)],
            'description': list(bindingToolStandardDescriptions)
        }
    )

    if not CSVfileName[-4:]=='.csv':
        CSVfileName += '.csv'

    bindingSheet.to_csv(CSVfileName, index=False)

    return {
        'bindingToolStandardDescriptions':bindingToolStandardDescriptions,
        'meta':metaMatrix[[metaMatrix.columns[x] for x in range(META_END_COLUMN_INDEX)]],
        'matrix':metaMatrix[[metaMatrix.columns[x] for x in range(MATRIX_START_COLUMN_INDEX, len(standardMetaMatrix.columns))]],
    }

def generateMetaData(bindingSheetPath:str, meta:pd.DataFrame, metaDataOutFilePath):

    metaFile = meta
    metaFile.columns = meta.columns.get_level_values(4)

    if not bindingSheetPath[-4:]=='.csv':
        bindingSheetPath += '.csv'

    bindingSheetData = pd.read_csv(bindingSheetPath)
    v_bools = pd.notna(bindingSheetData['dataTagId'])

    metaFile['dataTagId'] = bindingSheetData['dataTagId']

    metaFile = metaFile[v_bools]

    if not metaDataOutFilePath[-4:]=='.csv':
        metaDataOutFilePath += '.csv'

    metaFile.to_csv(metaDataOutFilePath, index=False)
    
    return metaFile

def getMissingTags(bindingSheetPath:str, tagMatrix, qcOutFileName='qcToolOutput'):

    if not bindingSheetPath[-4:]=='.csv':
        bindingSheetPath += '.csv'

    bindingSheetData = pd.read_csv(bindingSheetPath)

    # Requirement matrix (Fixed)
    R = np.array(tagMatrix)
    
    # get existence bool of dataTagId's 
    v_bools = pd.notna(bindingSheetData['dataTagId'])
    v_row = v_bools.replace({True:1, False:0})

    # convert into column vector
    v_col = []
    for v in v_row:
        v_col.append([v])

    # convert to numpy array
    v_col_np = np.array(v_col)
    
    # numpy rows of ones
    ones = np.ones(len(R[0]))

    # V = v*(1, 1, ...)
    V_int = v_col_np*ones
    V_bool = np.array(V_int, dtype=bool)
    V_bool

    # result matrix
    Z = np.logical_not(np.logical_or(np.logical_not(R), V_bool))

    # transpose to get details : by feature
    Z_prime = Z.transpose()

    qcDict = {}
    index = 0
    for feature in tagMatrix.columns:
        missingTagSeries = list(bindingSheetData['description'][Z_prime[index]])
        # filler :
        if len(missingTagSeries) < len(bindingSheetData['description']):
            diff = len(bindingSheetData['description']) - len(missingTagSeries)
            missingTagSeries += ['' for item in range(diff)]
        qcDict.update(
            {feature: missingTagSeries}
        )
        index += 1

    qcResult = pd.DataFrame.from_dict(qcDict)

    if not qcOutFileName[-4:]=='.csv':
        qcOutFileName += '.csv'

    qcResult.to_csv(qcOutFileName, index=False)
    
    return qcResult