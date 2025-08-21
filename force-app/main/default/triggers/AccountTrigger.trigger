trigger AccountTrigger on Account (before insert, before update, after insert, after update) {
    
    //Create Account --> Name is mandatory 
    //Create contact --> LastName is mandatory
    //Establish relation ship between Account and Contact --> On the contact Populate the accountId field with the account id --> where is the accountID coming from ?
      
    //Recurssion
    //Governor limits 
    //Order of execution
    
    if(trigger.isBefore && trigger.isInsert){
		AccountHandler.handleBeforeInsert(trigger.new);
	} 
    
    if(trigger.isAfter && trigger.isInsert){
        AccountHandler.handleAfterInsert(trigger.new);
    }
}


/*
  
  if(trigger.isBefore && trigger.isInsert){
		AccountHandler.handleBeforeInsert(trigger.new);
	} 
 
 if(trigger.isBefore && trigger.isInsert){
		AccountHandler.handleBeforeInsert(trigger.new);
	}
    else if(trigger.isBefore && trigger.isUpdate){
    	AccountHandler.handleBeforeUpdate(trigger.new, trigger.old, trigger.oldMap);
	}
    if(trigger.isAfter && trigger.isInsert){
        AccountHandler.handleAfterInsert(trigger.new);
    }
    else if(trigger.isAfter && trigger.isUpdate){
    	AccountHandler.handleAfterUpdate(trigger.new);
	}
*/

//invoke here the handler class
    //Trigger --> Handler class --> Helper Class 


  //ABC.bbc  
    //Dont execute Industry --> technology in update sceario
    //Perform a different logic in updat scenario
   //Trigger Context variables 
    
    
    //UI --> Enter data --> Save --> Control comes to Trigger --> data is in trigger.new --> send this data to handler class --> write Business logic --> saved to DB
    //Control
    //Data
    
    
    //Source to destination --> car --> Mustang
    //Costco --> Instacart --> House door step --> person --> refre
    //
    //Browser --> Trigger -->  DB --> vehicle --> trigger.new
    
    //Browser --> Trigger
 	//				trigger.new  --> BL --> DB
 	//				
 	//Broswer --> Trigger --> trigger.new --> Handler Class	--> BL			
    
   
    
    
    /*  
    List<Integer> lst = new List<Integer>();
    lst.add(3); // 0 
    lst.add(7); // 1
    lst.add(5); // 2 
    
    for(Integer abc : lst){
        system.debug('The elements in the list are : ' + abc);
    }
    */
   //trigger.new -- //lst --> variable containing all records
   //bbc -- //abc --> temporary variable name tha can hold data for each iteration
   //Account -- //Integer --> the type of data that is stored in the lst(List) variable
  /*  
    for(Account accRecord : trigger.new){
        system.debug('The account record from UI is : ' + accRecord);
        system.debug('The account record Name is : ' + accRecord.Name);        
        system.debug('The account record Owner is : ' + accRecord.OwnerId);
        
        system.debug('Industry value before : ' + accRecord.Industry);
        if(accRecord.Industry == null){
            accRecord.Industry = 'Technology';
        }
        system.debug('Industry value after : ' + accRecord.Industry);
        
    } 
*/