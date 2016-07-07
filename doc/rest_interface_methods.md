# List of REST interface methods

### Create new experiment
<strong>URL: </strong>/experiments  
<strong>Method: </strong>POST  
<strong>Headers: </strong> 

| Key | Description |  
| --- | ----------- |  
| experimenter | ID of the experimenter |  

<strong>JSON: </strong>  

| Key | Description |  
| --- | ----------- |  
| name | Name of the experiment |  
| experimentgroups | Names of the experiment groups |  
| size | Size of the experiment |  
| hypothesis | Hypothesis of the experiment |  
| start date | Start date of the experiment |  
| end date | End date of the experiment |  

<strong>Response: </strong> HTTP result code  

### List all experiments  
<strong>URL: </strong>/experiments  
<strong>Method: </strong>GET  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### Show specific experiment metadata 
<strong>URL: </strong>/experiments/{id}/metadata  
<strong>Method: </strong>GET  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### Delete experiment  
<strong>URL: </strong>/experiments/{id}  
<strong>Method: </strong>DELETE  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code  

### List configurations for specific user  
<strong>URL: </strong>/configurations  
<strong>Method: </strong>GET  
<strong>Headers: </strong>  

| Key | Description |  
| --- | ----------- |  
| username | Username of the user |  

<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### List all users  
<strong>URL: </strong>/users  
<strong>Method: </strong>GET  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### List all users for specific experiment  
<strong>URL: </strong>/experiments/{id}/users  
<strong>Method: </strong>GET  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### List all experiments for specific user  
<strong>URL: </strong>/users/{id}/experiments  
<strong>Method: </strong>GET  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code + JSON  

### Save experiment data  
<strong>URL: </strong>/events  
<strong>Method: </strong>POST  
<strong>Headers: </strong>  

| Key | Description |  
| --- | ----------- |  
| username | Username of the user |  

<strong>JSON: </strong>  

| Key | Description |  
| --- | ----------- |  
| key | Key of the experiment data |  
| value | Value of the experiment data |  

<strong>Response: </strong>HTTP result code  

### Delete user  
<strong>URL: </strong>/users/{id}  
<strong>Method: </strong>DELETE  
<strong>Headers: </strong>empty  
<strong>JSON: </strong>empty  
<strong>Response: </strong>HTTP result code  

