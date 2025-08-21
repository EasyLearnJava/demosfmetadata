public class AccountCallOutService {
    
    public static void getAllAccounts() {         
        try {
            String accessToken = AccountCallOutServiceHelper.getRequestToken();
            if (String.isNotBlank(accessToken)) {
                String endpoint = 'https://manageusers-dev-ed.my.salesforce.com/services/apexrest/sfaccounts';
                HttpResponse res = AccountCallOutServiceHelper.sendHttpRequest(accessToken, endpoint, 'GET', null);
                handleResponse(res);
            } else {
                system.debug('Access token is null or empty');
            }
        } catch(Exception e) {
            system.debug('Exception occurred: ' + e.getMessage());
        }        
    }
    
    public static void createAccount(String accName, String accPhone) {
        try {
            String accessToken = AccountCallOutServiceHelper.getRequestToken();
            if (String.isNotBlank(accessToken)) {
                String endpoint = 'https://manageusers-dev-ed.my.salesforce.com/services/apexrest/sfaccounts';
                String requestBody = '{"accountName":"' + accName + '", "accountPhone":"' + accPhone + '"}';
                HttpResponse res = AccountCallOutServiceHelper.sendHttpRequest(accessToken, endpoint, 'POST', requestBody);
                handleResponse(res);
            } else {
                system.debug('Access token is null or empty');
            }
        } catch(Exception e) {
            system.debug('Exception occurred: ' + e.getMessage());
        }        
    }
    
    public static void updateAccount(String accountId, String accOwnerShip, String accPhone) {
        try {
            String accessToken = AccountCallOutServiceHelper.getRequestToken();
            if (String.isNotBlank(accessToken)) {
                String endpoint = 'https://manageusers-dev-ed.my.salesforce.com/services/apexrest/sfaccounts/' + accountId;
                String requestBody = '{"accountOwnerShip":"' + accOwnerShip + '", "accountPhone":"' + accPhone + '"}';
                HttpResponse res = AccountCallOutServiceHelper.sendHttpRequest(accessToken, endpoint, 'PUT', requestBody);
                handleResponse(res);
            } else {
                system.debug('Access token is null or empty');
            }
        } catch(Exception e) {
            system.debug('Exception occurred: ' + e.getMessage());
        }        
    }
    
    public static void deleteAccount(String accountId) {
        try {
            String accessToken = AccountCallOutServiceHelper.getRequestToken();
            if (String.isNotBlank(accessToken)) {
                String endpoint = 'https://manageusers-dev-ed.my.salesforce.com/services/apexrest/sfaccounts/' + accountId;
                HttpResponse res = AccountCallOutServiceHelper.sendHttpRequest(accessToken, endpoint, 'DELETE', null);
                handleResponse(res);
            } else {
                system.debug('Access token is null or empty');
            }
        } catch(Exception e) {
            system.debug('Exception occurred: ' + e.getMessage());
        }        
    }
    
    private static void handleResponse(HttpResponse res) {
        if (res != null) {
            if (res.getStatusCode() == 200) {
                String responseBody = res.getBody();
                system.debug('Response : ' + responseBody);
            } else {
                String errorMessage = 'Error: ' + res.getStatusCode() + ' - ' + res.getStatus() + '\n' + res.getBody();
                system.debug(errorMessage);
            }
        } else {
            system.debug('Response is null');
        }
    }
}