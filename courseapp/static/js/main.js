function enrollSection(){
    let selected = document.querySelector('input[name="section"]:checked')

    if (!selected){
        alert('Vui lòng chọn lớp trước khi đăng ký')
        return
    }

    fetch('/api/enroll-section', {
        method: "POST",
        body: JSON.stringify({
            "section_id" : selected.value,
            "price" : selected.dataset.price,
            "schedule" : selected.dataset.schedule,
            "classroom_name" : selected.dataset.classroom_name,
            "course_name" : selected.dataset.course_name
        }),
        headers: {
            "Content-Type" : "application/json"
        }
    }).then(res => res.json()).then(data => {
        alert(data.message)

        location.reload()
    })
}


function cancelSection(enrollment_existed_id){

    fetch('/api/cancel-section', {
        method: "PATCH",
        body: JSON.stringify({
            "id": enrollment_existed_id
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        alert(data.message)

        location.reload()
    })
}

