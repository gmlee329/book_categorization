// var select = document.getElementById('selector');
var outputbox = document.getElementById('outputbox');
var output_category = document.getElementById('output_category');
var output_accuracy = document.getElementById('output_accuracy');
var submit = document.getElementById("submit");
var input_text = document.getElementById('input_text');
var initial_text = ["예측 카테고리 : ", "정확도 : "];
// initial()

// function initial() {
//     var counts = [3, 5];
//     for (var i = 0; i < counts.length; i++) {
//         var count = counts[i];
//         var option = document.createElement("option");
//         option.textContent = count;
//         option.value = count;
//         select.appendChild(option);
//     }
// }

function set_outputtext_innerHTML(initial_text, category, accuracy) {
    output_category.innerHTML = initial_text[0] + category;
    output_accuracy.innerHTML = initial_text[1] + accuracy;
}

function set_submit_disabled(is_disable) {
    submit.disabled = is_disable;
}

function upload_result(result) {
    set_outputtext_innerHTML(initial_text, result['category'], result['accuracy']+'%');
    var books = result['books'];
    // var count = parseInt(select.options[select.selectedIndex].value);
    for (var book of books) {
        var div = document.createElement('div');
        var img = document.createElement('img');
        var title = document.createElement('div');
        var link = document.createElement('a');

        div.style.cssText = 'display: flex\; flex-direction: column\; justify-content: start\; align-items: center\; padding-left: 10px\; padding-right: 10px\;';
        div.style.width = String(parseInt(100/3)) + "%";
        // div.style.width = String(parseInt(100/count)) + "%";
        link.href = book['link'];
        link.target = '_blank';
        link.style.width = '100%';
        img.src = book['imgURL'];
        img.style.width = '100%';
        link.appendChild(img);
        title.innerHTML = book['title'];
        title.style.cssText = 'text-align: center\; margin-top: 10px';
        div.appendChild(link);
        div.appendChild(title);
        outputbox.appendChild(div);
    }
}

function handle_error(e) {
    set_outputtext_innerHTML(initial_text, e, '');
    set_submit_disabled(false);
}

document.getElementById("submit").onclick = () => {
    $("#outputbox").empty();
    set_submit_disabled(true);
    set_outputtext_innerHTML(initial_text, '', '');

    var content = input_text.value;
    try {
        if (content == undefined) {
            throw Error("도서 내용을 입력해주세요.");
        }
        content = content.trim();
        if (content == '') {
            throw Error("도서 내용을 입력해주세요.");
        }
    } catch (e) {
        handle_error(e)
        return;
    }

    const formData = new FormData();
    formData.append('content', content)

    fetch(
        '/prediction',
        {
            method: 'POST',
            body: formData,
        }
    )
        .then(async response => {
            if (response.status == 200) {
                return response
            }
            else if (response.status == 413) {
                throw Error("Text content is too long for the server to process.")
            }
            else {
                throw Error((await response.clone().json()).message)
            }
        })
        .then(response => response.json())
        .then(result => {
            upload_result(result);
            set_submit_disabled(false);
        })
        .catch(e => {
            handle_error(e)
        })
}