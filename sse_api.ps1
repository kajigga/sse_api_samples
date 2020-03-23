# This first line was needed because windows wasn't recognizing the TLS cert
# (LetsEncrypt) on my SSE server. Perhaps it is unnecesary in practice
# [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls -bor [Net.SecurityProtocolType]::Tls11 -bor [Net.SecurityProtocolType]::Tls12
#
# This script has been tested with PowerShell 6.1 and 6.2

# Set the SSEAPI_USERNAME, $SSEAPI_PASSWORD, and $SSEAPI_HOSTNAME values in environmental variables
# SSEAPI_HOSTNAME must include https:// 

# $env:SSEAPI_USERNAME
# $env:SSEAPI_PASSWORD
# $env:SSEAPI_HOSTNAME

$script:AuthenticatedSession = $null
function SSEAPI-Login {
    Param(
        $username,
        $password,
        $hostname
    )
    # Only login once per session
    if($script:AuthenticatedSession -eq $null){

        if($hostname -eq $null){
            $hostname = $env:SSEAPI_HOSTNAME
        }
        if($username -eq $null){
            $username = $env:SSEAPI_USERNAME
        }
        if($password -eq $null){
            $password = $env:SSEAPI_PASSWORD
        }

        Write-Output @{
            hostname=$hostname;
            username=$username;
            password=$password
        }

        $secpassword = ConvertTo-SecureString $password -AsPlainText -Force

        $credentials = New-Object System.Management.Automation.PSCredential($username, $secpassword)

        $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username,$password)))

        $login_uri = "$hostname/account/login"
        
        $props = @{
         Uri=$login_uri;
         Credential = $credentials;
         Method="Get"
        }

        $WebSession = $null
        $resp = Invoke-RestMethod @props -SessionVariable WebSession

        $hdrs = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
        $hdrs['X-Xsrftoken'] = $WebSession.Cookies.GetCookies($login_uri)[0].Value
        $hdrs['Authorization'] = "Basic $base64AuthInfo"
       
        $script:AuthenticatedSession = new-object psobject -Property @{
            web_session=$WebSession;
            credentials=$credentials;
            headers=$hdrs
        }
    }
    $script:AuthenticatedSession
}

function SSEAPI-Request {
    Param(
        $resource,
        $method,
        $kwarg,
        $username,
        $password,
        $hostname
    )

    $auth = SSEAPI-Login

    # $resource should be in the form of '<resource>.<method>'. 
    # For example 'admin.trim_database' or 'api.get_versions'
    $resource_parts = $resource -split "\."   
    
    $api_body = @{
        resource=$resource_parts[0];
        method=$resource_parts[1];
        kwarg=$kwarg} | ConvertTo-Json

    $props = @{
        Uri="$ENV:SSEAPI_HOSTNAME/rpc";
        Headers=$auth.headers;
        Method='Post';
        Credential=$auth.credentials;
        Body=$api_body;
        WebSession=$auth.web_session
    }

    $response = Invoke-RestMethod @props

    New-Object psobject -property @{
       response=$response;
       session=$auth
    }
}

SSEAPI-Request -resource "admin.trim_database" -kwarg @{"audit"=1} 
