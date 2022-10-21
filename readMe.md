### import binding tool
`from tools import bindingAndQC`

### get config template
`bindingAndQC.config`

### generate binding template

`result1 = bindingAndQC.generateTemplate(config, 'SITE_TAG_BINDING')`

```
{
    'super heater exists': True,
    'Boiler type [RG=1, FBC=2]': 1,
    'fuel totaliser unit': 'KG',
    'steam totaliser unit': 'KG',
    'water totaliser unit': 'KG',
    'load brackets': 5,
    'Number of grates/beds': 1,
    'PRIMARY DAMPER': {'instances': 1},
    'SECONDARY DAMPER': {'instances': 1},
    'GT SCREW': {'instances': 1},
    'SA FAN': {'instances': 1},
    'BUCKET ELEVATOR': {'instances': 1},
    'ROTARY FEEDER': {'instances': 1},
    'FEED WATER PUMP': {'instances': 1},
    'CRUSHER': {'instances': 1},
    'FW PUMP': {'instances': 1},
    'HYDRAULIC POWER PACK': {'instances': 1},
    'DUST COLLECTOR': {
        'instances': 1, 
        'RAV': {'instances': 1}
        },
    'RAM PUSHER': {'instances': 1},
    'ASH SCREW': {'instances': 1},
    'FD FAN': {'instances': 1},
    'SLAT CONVEYOR': {'instances': 1},
    'DUST EXTRACTION FAN': {'instances': 1},
    'SECONDARY FD FAN': {'instances': 1},
    'FUEL SCREW': {'instances': 1},
    'BOOSTER FAN': {'instances': 1},
    'SCREW FEEDER': {'instances': 1},
    'GRATE': {
        'TROLLEY': {'instances': 1}
        }
}
```

### generate meta data
`result2 = bindingAndQC.generateMetaData('SITE_TAG_BINDING', result1['meta'], 'SITE_META_DATA')`

### generate qc report
`result3 = bindingAndQC.getMissingTags('SITE_TAG_BINDING', result1['matrix'], 'SITE_QC')`
