public class AccountHandler {
    
    //Sequential 
    
    public static void handleBeforeInsert(List<Account> newAccounts){        
        for(Account accRecord : newAccounts){
            system.debug('Account ID : ' + accRecord.Id); 
        }         
    }
    
   public static void handleAfterInsert(List<Account> newAccounts){ 
		List<Contact> conList = new List<Contact>();   
       Set<Id> accIds = new Set<ID>();
        for(Account accRecord : newAccounts){            
            system.debug('Account ID : ' + accRecord.Id);            
            Contact con = new Contact(FirstName = 'First', LastName = accRecord.Name, AccountId = accRecord.Id);
            conList.add(con); 
            accIds.add(accRecord.Id);
        } 
       insert conList;
       AnimalCallOutService.getAnimalDetailsForAccount(accIds);
       
       
    } 
    
    //UI --> enter data --> hit save button --> Trigger before insert --> write all business logic  --> Store in  Database --> Call after insert
    //If type == prospect --> I cannot change it to technilogy partner, if type != prospect i can change is to technology partner
    //Map
    
    //Type -> prospect --> abc ?
    //Type -> prospect --> bbc ?
    //Type -> prospect --> Other ? 
    
  /*   public static void handleBeforeInsert(List<Account> newAccounts){        
        for(Account accRecord : newAccounts){
            if(String.isBlank(accRecord.Industry)){
                accRecord.Industry = 'Technology';
            }
        }         
    }
    
    public static void handleBeforeUpdate(List<Account> newAccounts, List<Account> oldAccounts, Map<Id, Account> oldMap){        
        
        //In Before Update do we have id for all the records coming in to this method ? --> Yes
        //What will newAccounts contain ? --> Contains Updated account records
        //What will oldAccounts contain ? --> Contains old data before the user updated the record or contains the data present in the database
        //What will oldMap contain ? --> all key value pairs,  ID and Account record pair 
        for(Account acc : newAccounts){
            if(oldMap.get(acc.id).Type == 'Prospect' && acc.Type == 'Other'){
                acc.addError('Prospect cannot be changed to Other');
            }     
        }
        //Id temp = '001al000002FXtoAAG';
        system.debug('Contents of Map : ' + oldMap.get('001al000002FXtoAAG'));
        system.debug('Contents of Map Type : ' + oldMap.get('001al000002FXtoAAG').Type);
        
        */
        
        
        /*for(Account accRecord : newAccounts){
            if(accRecord.NumberOfEmployees == null){
                accRecord.NumberOfEmployees = 5;
            }
            system.debug('Before update new accRecord : ' + accRecord);
        }      
        for(Account accRecord : oldAccounts){
            system.debug('Before update old accRecord : ' + accRecord);
        }      
    } */
    
    //I will create a contact by default for every account
 /*   public static void handleAfterInsert(List<Account> newAccounts){        
        for(Account accRecord : newAccounts){
            system.debug('Insert accRecord : ' + accRecord);
        }         
    } 
    
    public static void handleAfterUpdate(List<Account> newAccounts){        
        for(Account accRecord : newAccounts){
            system.debug('After update accRecord : ' + accRecord);
        }         
    } */
    
}