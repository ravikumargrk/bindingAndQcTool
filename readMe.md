### import binding tool
```
from tools import bindingAndQC
```

### get config template
```
bindingAndQC.config
```

### generate binding template

```
result1 = bindingAndQC.generateTemplate(config, 'SITE_TAG_BINDING')
```

### generate meta data
```
result2 = bindingAndQC.generateMetaData('SITE_TAG_BINDING - Copy.csv', result1['meta'], 'SITE_META_DATA')
```

### generate qc report
```
result3 = bindingAndQC.getMissingTags('SITE_TAG_BINDING', result1['matrix'], 'SITE_QC')
```
