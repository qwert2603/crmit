function makeStateSwitcher(stateContainer) {
    const radios = stateContainer.getElementsByTagName('input');
    const stateTexts = stateContainer.getElementsByClassName('state_text');

    let state = 0;
    for (let i = 0; i < radios.length; ++i) {
        if (radios[i].checked) {
            state = i;
            break;
        }
    }

    function render(state) {
        radios[state].checked = true;
        for (let i = 0; i < stateTexts.length; ++i) {
            stateTexts[i].style.display = "none";
        }
        stateTexts[state].style.display = "inline";
    }

    stateContainer.onclick = function () {
        state = (state + 1) % radios.length;
        render(state)
    };
    render(state);
}

const stateContainers = document.getElementsByClassName('state_container');
for (let i = 0; i < stateContainers.length; ++i) {
    makeStateSwitcher(stateContainers[i]);
}