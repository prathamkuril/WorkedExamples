

declare var artoo: any;
declare var chrome: any;
declare var axios: any;

// Use Artoo to scrape the cumulative text
if (typeof artoo !== 'undefined') {

   /*
    let NN = 1024*100; // we only have an 8k buffer, 100k string is 12 calls to LLM then another to summarise that. 
    let haveSummary = false;
    let baseSummaryText = "Summarising ...";
    let haveClassification = false;
    let baseClassificationText = "Classifying ...";
    let allText = "";

    let interval = setInterval (() => {

      if (!haveSummary || !haveClassification) {

         if (!haveSummary) {
            baseSummaryText = baseSummaryText + ".";
            chrome.runtime.sendMessage({type: "Summary", text: baseSummaryText});       
         }

         if (!haveClassification) {
            baseClassificationText = baseClassificationText + ".";
            chrome.runtime.sendMessage({type: "Classification", text: baseClassificationText});       
         }

      }
      else {
         clearInterval (interval);
      }
    }, 1000);

    setTimeout (() => {

      try {
         // First try to get all plain text, if that doesnt work, get the headers
         var scraped = artoo.scrape('p', 'text');
         if (scraped.length === 0) {
            for (var i = 0; i < 6; i++) {
               scraped = scraped = artoo.scrape('h' + i.toString(), 'text');
            }
         }
      
         allText = scraped.join(' \n');

         if (allText.length > NN) 
            allText = allText.substring(0, NN);
      }
      catch {
         allText = "";
      }

      var summarizeQuery = 'https://braidapi.azurewebsites.net/api/summarize?session=49b65194-26e1-4041-ab11-4078229f478a';
      var classifyQuery = 'https://braidapi.azurewebsites.net/api/classify?session=49b65194-26e1-4041-ab11-4078229f478a';

      axios.post(summarizeQuery, {
         data: {
            text: allText
         },
         headers: {
            'Content-Type': 'application/json'
         }
      }).then ((summaryRes: any) => {
         haveSummary = true;          
         if (summaryRes.status === 200) {
            chrome.runtime.sendMessage({type: "Summary", text: summaryRes.data});
            
            axios.post(classifyQuery, {
               data: {
                  text: summaryRes.data
               },
               headers: {
                  'Content-Type': 'application/json'
               }
            }).then ((classifyRes: any) => {
               haveClassification = true;          
               if (classifyRes.status === 200) {
                  chrome.runtime.sendMessage({type: "Classification", text: classifyRes.data});
               } 
               else {
                  chrome.runtime.sendMessage({type: "Classification", text: "Sorry, could not fetch a classification from the Waterfall server."}); 
               }
            })
            .catch ((e : any) => {     
               haveClassification = true;  
               console.error (e);   
               chrome.runtime.sendMessage({type: "Classification", text: "Sorry, could not fetch a classification from the Waterfall server."});                 
            });        
         } 
         else {
            haveSummary = true;  
            haveClassification = true;   
            chrome.runtime.sendMessage({type: "Summary", text: "Sorry, could not fetch a summary from the Waterfall server."}); 
            chrome.runtime.sendMessage({type: "Classification", text: "Sorry, could not fetch a classification from the Waterfall server."}); 
         }
      })
      .catch ((e: any) => {     
         haveSummary = true;  
         haveClassification = true;
         console.error (e);   
         chrome.runtime.sendMessage({type: "Summary", text: "Sorry, could not fetch a summary from the Waterfall server."});                 
         chrome.runtime.sendMessage({type: "Classification", text: "Sorry, could not fetch a classification from the Waterfall server."}); 
      });   

    }, 500);
    */
}