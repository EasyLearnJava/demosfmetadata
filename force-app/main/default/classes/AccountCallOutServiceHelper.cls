public class AccountCallOutServiceHelper {
    
    public class resWrapper
    {
        public String id;
        public String access_token;
    }
    
    public static String getRequestToken(){
        
        //Get custom settings:
        ManageUsersOrgSettings__c orgSettings = [SELECT LoginURL__c, InstanceURL__c, clientId__c, clientSecret__c, username__c, password__c FROM ManageUsersOrgSettings__c where OrgName__c = 'manageusers'];
       
        String reqbody = 'grant_type=password'+'&client_id='+orgSettings.clientId__c+'&client_secret='+orgSettings.clientSecret__c+'&username='+orgSettings.username__c+'&password='+orgSettings.password__c;
        //String reqbody = 'grant_type=authorization_code'+'&client_id='+orgSettings.clientId__c+'&client_secret='+orgSettings.clientSecret__c+'&username='+orgSettings.username__c;
        Http h1 = new Http();
        HttpRequest req = new HttpRequest();
        req.setBody(reqbody);
        req.setMethod('POST');
        req.setEndpoint('https://login.salesforce.com/services/oauth2/token');
        HttpResponse res = h1.send(req);
        resWrapper response = (resWrapper)JSON.deserialize(res.getBody(),resWrapper.class);
        System.debug('response--->>>'+response);
        return response.access_token;
    }
    
    //below method has some issue, OAuthTokenFetcher is working class
    public static String getRequestTokenv2(){
        
        //Get custom settings:
        ManageUsersOrgSettings__c orgSettings = [SELECT LoginURL__c, InstanceURL__c, clientId__c, clientSecret__c, username__c, password__c FROM ManageUsersOrgSettings__c where OrgName__c = 'manageusers'];
       
        String cid = '3MVG9fnmEuvG9uRNA5LciEB_NzwYMIKMhCuU9FPBuljNqdDU6RpkCM.nF.jL4zRK1iY5xGSn_wLdNJQOKa3if';
        string cs = 'CBD4D0C1C8958C508B8C2411D8AF5B4C602AC48BD1A504D82F0C4A9B565555A3';
        String reqbody = 'grant_type=client_credentials'+'&client_id='+cid+'&client_secret='+cs;
        String body = 'client_id='+cid+
                      '&client_secret='+cs+
                      '&grant_type=client_credentials';
        Http h1 = new Http();
        HttpRequest req = new HttpRequest();
        req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
        req.setBody(body);
        req.setMethod('POST');
        req.setEndpoint('https://dynegy--raghudev.sandbox.my.salesforce.com/services/oauth2/token');
        HttpResponse res = h1.send(req);
        resWrapper response = (resWrapper)JSON.deserialize(res.getBody(),resWrapper.class);
        System.debug('response--->>>'+response);
        return response.access_token;
    }
    
    public static HttpResponse sendHttpRequest(String accessToken, String endpoint, String method, String requestBody) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint); 
        req.setMethod(method);
        req.setHeader('Authorization', 'Bearer ' + accessToken);
        req.setHeader('Content-Type', 'application/json');
        req.setHeader('Accept', 'application/json');
        if (method != 'GET' && method != 'DELETE') {
            req.setBody(requestBody);
        }
        
        Http http = new Http();            
        return http.send(req);
    }
    
   /*    public static String getAccessToken() {
        // Get custom settings
        ManageUsersOrgSettings__c orgSettings = [SELECT LoginURL__c, InstanceURL__c, clientId__c, clientSecret__c, username__c, password__c, jwtPrivateKey__c FROM ManageUsersOrgSettings__c where OrgName__c = 'manageusers'];

        // Generate the JWT token
        String jwtToken = generateJWTToken(orgSettings.clientId__c, orgSettings.username__c, orgSettings.jwtPrivateKey__c);

        // Exchange the JWT token for an access token
        String accessToken = exchangeJWTForAccessToken(orgSettings.clientId__c, orgSettings.clientSecret__c, jwtToken, orgSettings.LoginURL__c);

        return accessToken;
    }
    
    
 private static String generateJWTToken(String clientId, String username, String jwtPrivateKey) {
        // Generate the JWT token using the provided client ID, username, and private key
        // This code will vary depending on the JWT library you use
        // Example using the 'jwt-handler' library:
        Jwt jwt = new Jwt();
        jwt.setIssuer(clientId);
        jwt.setSubject(username);
        jwt.setAudience('https://login.salesforce.com');
        jwt.setExpirationTime(System.now().addSeconds(300)); // Token expires in 5 minutes
        return jwt.sign(jwtPrivateKey);
    }
    
    private static String exchangeJWTForAccessToken(String clientId, String clientSecret, String jwtToken, String loginUrl) {
        // Exchange the JWT token for an access token
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(loginUrl + '/services/oauth2/token');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
        req.setBody('grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=' + jwtToken);
        //req.setHeader('Authorization', 'Basic ' + EncodingUtil.base64Encode(clientId + ':' + clientSecret));

        HttpResponse res = http.send(req);
        Map<String, Object> responseMap = (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
        return (String)responseMap.get('access_token');
    }
*/
}