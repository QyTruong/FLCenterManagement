function classRegisterModal(courseId){
//    event.preventDefault()

    fetch(`/api/class-list/${courseId}`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        classes = data

        let area = document.getElementById("classListArea")

        let html = ''

        classes.forEach(c => {
            let i = 0

            let scheduleText = ''

            for (let s of c.schedules){
                scheduleText += s.day_of_week

                if (i === c.schedules.length-1)
                    scheduleText += ': ' + s.start_time + ' - ' + s.end_time
                else
                    scheduleText += ' - '
                i += 1
            }

            html += `
                <tr>
                    <td> ${c.name} </td>
                    <td> ${scheduleText} </td>
                    <td> .../${c.max_student}</td>
                    <td><input type="radio" name="class_id" value="${c.id}"></td>
                </tr>
            `
        })
        area.innerHTML = html;
    })
}
