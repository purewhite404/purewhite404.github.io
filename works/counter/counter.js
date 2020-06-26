let count = 1

const countUp = () => {
        count *= 2
        const countElement = document.querySelector('#count')
        countElement.innerText = '回数: ' + count

        title =''
        const initialMoveTitle = document.querySelector('#title')
        initialMoveTitle.innerText = 'カウンターです（2倍）'
}
