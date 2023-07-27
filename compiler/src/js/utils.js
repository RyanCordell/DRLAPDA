
export const getEle = (ele, returnFirst = true) => (returnFirst) ? document.getElementsByClassName(ele)[0] : document.getElementsByClassName(ele);
export const getEleByID = (ele) => document.getElementById(ele);
export const printDebugLine = (val) => getEle('debug-field').innerHTML += val + '<br><br>';