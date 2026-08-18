var id = null;
var config_sync = {};
var themes = {};

var homepage = function () {return chrome.runtime.getManifest().homepage_url};
var version = function () {return chrome.runtime.getManifest().version};
const url = "/data/popup/index.html";


var initListeners = () => {
    chrome.runtime.onInstalled.addListener(function(details){
        if(details.reason == "install"){
            onInstall();
        }

        
    });
    
    chrome.action.onClicked.addListener(function(activeTab)
    {
        chrome.tabs.create({ url: url });
    });

    chrome.storage.onChanged.addListener(function (changes, namespace) {
    });


}

var onInstall = function(){
    chrome.storage.sync.set({
        currentTheme: "day",
        di: (new Date()).getTime()
    });

}

var Background = (function(){

    console.log('background constructor');

    initListeners();

      
})();
