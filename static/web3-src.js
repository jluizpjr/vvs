var Web3 = require("web3")

//Trying to connect direct to a node
//const web3 = new Web3("https://bsc-dataseed.binance.org")

//Trying to use Metamask instead
const web3 = new Web3(window.ethereum)


//####################### Get Account #######################
const enableMetaMaskButton = document.getElementById('enableMetaMaskButton');
const showAccount = document.getElementById('walletAddress');

enableMetaMaskButton.addEventListener('click', () => {
  console.log("Enabling MetaMask")
  getAccount();
});

async function getAccount() {
  try {
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
    const account = accounts[0];
    enableMetaMaskButton.disabled = true;
    voteButton.disabled = false; 
    showAccount.innerHTML = "Wallet=" + account;
    return account;
  }
  catch (err) {
    alert(err.message);
  };
}

//###################### Vote Action ######################

const wallet_Address = document.getElementById("wallet_Address");
const voteButton = document.getElementById('voteButton');
const signature = document.getElementById('signature');

voteButton.addEventListener('click', () => {
    console.log("Calling Vote function")
    vote();
  });
  
async function vote(){
    const account = await getAccount();
    //alert(account);
    wallet_Address.value = account;
    var checked = document.getElementsByClassName("form-check-input");
    console.log("Volunteers id:" + checked);
    var arr = [];

    for (let i = 0; i < checked.length; i++) {
        arr.push(checked[i].value+' ');
    }


    // Sign content

    //await web3.eth.personal.sign('I\'m voting for: '+arr, account);
    signature.value = await web3.eth.personal.sign('I\'m voting for Community Volunteer of the month.', account);
    document.getElementById('form').submit();

    

  }



//###################### Sign Message ######################