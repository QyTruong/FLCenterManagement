function enrollSection(){
    let selectedSection = document.querySelector('input[name="section"]:checked')

    if (!selectedSection){
        alert('Vui lòng chọn lớp trước khi đăng ký')
        return
    }

    fetch('/api/enroll-section', {
        method: "POST",
        body: JSON.stringify({
            "section_id" : selectedSection.value
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

