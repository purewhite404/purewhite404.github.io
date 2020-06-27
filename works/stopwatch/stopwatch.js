const toggle = () => {
        // スタートボタンを押したときの開始時刻 これが基準時刻となる
        const originDate = Date.now()

        const stopwatch = document.querySelector('#stopwatch')
        // ストップは一時停止 再開するときに表示されている時刻を取得しなければならない
        const continuefrom = Number(stopwatch.innerText)

        const toggleButton = document.getElementById('toggle')
        const buttonText = document.querySelector('#toggle')

        switch (toggleButton.className){
                case 'start':
                        buttonText.innerText = 'ストップ'
                        intervalId = setInterval(() =>
                                stopwatch.innerText = ((Date.now() - originDate)/1000 + continuefrom).toFixed(3),
                                1)
                        toggleButton.className = 'stop'
                        break
                case 'stop':
                        clearInterval(intervalId)
                        buttonText.innerText = 'スタート'
                        toggleButton.className = 'start'
                        break
                default:
                        console.error(`Error: Nothing class "${toggleButton.className}"`)
        }
}

const reset = () => {
        const stopwatch = document.querySelector('#stopwatch')
        stopwatch.innerText = 0
}
