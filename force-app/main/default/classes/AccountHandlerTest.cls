@isTest
public class AccountHandlerTest {
    
    @isTest
    public static void handleBeforeInsertBlankTest(){
        Account acc = new Account(Name='Demo Account'); 
        insert acc;        
        acc = [select Industry from Account where Id = :acc.Id];
        System.assertEquals('Technology', acc.Industry); 
    }
    
    @isTest
    public static void handleBeforeInsertNonBlankTest(){
        Account acc = new Account(); 
        acc.Name = 'Test Account';
        acc.Industry = 'Agriculture';
        insert acc; 
        acc = [select Industry from Account where Id = :acc.Id];
        System.assertEquals('Agriculture', acc.Industry);
    }    
}