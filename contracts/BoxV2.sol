// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract BoxV2 {
    uint256 public value;

    event ValueChanged(uint256 newValue);

    function store(uint256 _newValue) public {
        value = _newValue;
        emit ValueChanged(_newValue);
    }

    function retrieve() public view returns (uint256) {
        return value;
    }

    function increment() public {
        value += 1;
        emit ValueChanged(value);
    }
}
/**
    Dentro de Proxy Admin tenes una funcion llamada upgrade para cambiar la implementacion
    Y otra llamada upgradeAndCall. Cambia la implementacion del proxy y ademas llama a una funcion 'initializer'
    Es como un constructor, podria ser cualquier funcion. Por que? i dunno, investigate 
*/
