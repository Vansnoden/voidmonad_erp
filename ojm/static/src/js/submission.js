$(document).ready(() => {

    // var editor = new Quill('.meditor');
    let charLimit = 300;

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function myPopFunction() {
        var popup = document.getElementById("myPopup");
        popup.classList.toggle("show");
    }

    $(".mpopup").click((ev) => {
        let source = ev.target || ev.srcElement;
        let text = source.children[0];
        text.classList.toggle("show");
    })

    try{
        var Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }catch(error){
        console.error(error);
    }


    try {
        $('#article_full_title').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                // ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ]
        });

        $('#article_abstract').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ],
            placeholder: 'Your abstract should have 250 words to 300 at most',
            callbacks: {
                onKeydown: function(e) {
                    let characters = $('#article_abstract').summernote('code').replace(/(<([^>]+)>)/ig, "");
                    let totalCharacters = characters.split(' ').length;
                    $("#total-characters").text(totalCharacters + " / " + charLimit);
                    var t = e.currentTarget.innerText;
                    if (t.split(' ').length >= charLimit) {
                        if (e.keyCode != 8 && !(e.keyCode >= 37 && e.keyCode <= 40) && e.keyCode != 46 && !(e.keyCode == 88 && e.ctrlKey) && !(e.keyCode == 67 && e.ctrlKey)) e.preventDefault();
                    }
                },
                onKeyup: function(e) {
                    var t = e.currentTarget.innerText;
                    $('#article_abstract').text(charLimit - t.split(' ').length);
                },
                onPaste: function(e) {
                    let characters = $('#article_abstract').summernote('code').replace(/(<([^>]+)>)/ig, "");
                    let totalCharacters = characters.split(' ').length;
                    $("#total-characters").text(totalCharacters + " / " + charLimit);
                    var t = e.currentTarget.innerText;
                    var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');
                    e.preventDefault();
                    var maxPaste = bufferText.split(' ').length;
                    if (t.split(' ').length + bufferText.split(' ').length > charLimit) {
                        maxPaste = charLimit - t.split(' ').length;
                    }
                    if (maxPaste > 0) {
                        document.execCommand('insertText', false, bufferText);
                    }
                    $('#total-characters').text(charLimit - t.split(' ').length +" / "+ charLimit);
                }
            }
        });

        $('#highlights').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ]
        });
        $('#funding').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ]
        });
        $('#rcomment').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ]
        });
        $('#acomment').summernote({
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'italic']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['insert', ['link']],
                ['view', ['fullscreen', 'help']],
                ['specialchars']
            ]
        });

    } catch (error) {
        console.error(error);
        // Expected output: ReferenceError: nonExistentFunction is not defined
        // (Note: the exact output may be browser-dependent)
    }


    $('#cauthor').select2();

    $("#affiliations").select2();


    $("#close_author_1").click(() => {
        $("#author_1").remove();
    });

    $("#close_reviewer_1").click(() => {
        $("#reviewer_1").remove();
    });


    $("#new_main_file_input").change(() => {
        alert("Are you sure? your previous main file will be replaced .");
    })


    $("#save_declaration").click(()=>{
        $('.btn_save_declaration').removeClass("btn-primary");
        $('.btn_save_declaration').addClass("btn-secondary");
        $('.btn_save_declaration').attr("disabled", "1");
        $('#form-author-dec')[0].checkValidity();
        let isValid = $('#form-author-dec')[0].reportValidity();
        if (isValid) {
            $('#form-author-dec')[0].submit();

            const refresh = ()=>{
                Toast.fire({
                    icon: 'success',
                    title: 'Declaration saved'
                });
                $('.btn_save_declaration').removeClass("btn-secondary");
                $('.btn_save_declaration').addClass("btn-primary");
                $('.btn_save_declaration').removeAttr("disabled");
                
                $("#modal-author-dec").modal('hide');
                $("#declaration-toggler").addClass('d-none');
                $("#submit_conf").removeClass('d-none');
            } 
            setTimeout(refresh, 3000);
        }
    })

    $("#add_reviewer").click(() => {
        // check fields validity
        $('#form_add_reviewer')[0].checkValidity();
        let isValid = $('#form_add_reviewer')[0].reportValidity();
        if (isValid) {
            $('#form_add_reviewer')[0].submit();
            $('.btn_add_reviewer').removeClass("btn-primary");
            $('.btn_add_reviewer').addClass("btn-secondary");
            $('.btn_add_reviewer').attr("disabled", "1");
            const getReviewers = function () {
                refreshReviewers();
                $("#info-box").removeClass('d-none');
                $("#form_add_reviewer")[0].reset();
                Toast.fire({
                    icon: 'success',
                    title: 'Reviewer added successfully'
                });
                $('.btn_add_reviewer').removeClass("btn-secondary");
                $('.btn_add_reviewer').addClass("btn-primary");
                $('.btn_add_reviewer').removeAttr("disabled");
            }
            setTimeout(getReviewers, 3000);
        }
    })

    $("#upload_data_btn").click(function (ev) {
        $('#form-upload')[0].checkValidity();
        let isValid = $('#form-upload')[0].reportValidity();
        if (isValid) {
            $('#form-upload')[0].submit();
            $('.btn_add_file').removeClass("btn-primary");
            $('.btn_add_file').addClass("btn-secondary");
            $('.btn_add_file').attr("disabled", "1");

            const getFiles = function () {
                refreshFiles();
                $("#form-upload")[0].reset();
                $("#info-box").removeClass('d-none');
                Toast.fire({
                    icon: 'success',
                    title: 'File uploaded successfully'
                });
                $('.btn_add_file').removeClass("btn-secondary");
                $('.btn_add_file').addClass("btn-primary");
                $('.btn_add_file').removeAttr("disabled");
            }
            setTimeout(getFiles, 3000);
        }
    });


    $("#add_aff").click(() => {
        $('#form_add_aff')[0].checkValidity();
        let isValid = $('#form_add_aff')[0].reportValidity();
        if (isValid) {
            $('#form_add_aff')[0].submit();
            $('.btn_add_aff').removeClass("btn-primary");
            $('.btn_add_aff').addClass("btn-secondary");
            $('.btn_add_aff').attr("disabled", "1");
            const getAffs = function () {
                refreshAffs();
                $("#form_add_aff")[0].reset();
                $("#info-box").removeClass('d-none');
                Toast.fire({
                    icon: 'success',
                    title: 'affiliation added successfully'
                });
                $('.btn_add_aff').removeClass("btn-secondary");
                $('.btn_add_aff').addClass("btn-primary");
                $('.btn_add_aff').removeAttr("disabled");
            }
            setTimeout(getAffs, 3000);
        }
    }) 

    $("#add_author").click(() => {
        // check fields validity
        $('#form_add_author')[0].checkValidity();
        let isValid = $('#form_add_author')[0].reportValidity();
        if (isValid) {
            $('#form_add_author')[0].submit();
            $('.btn_add_author').removeClass("btn-primary");
            $('.btn_add_author').addClass("btn-secondary");
            $('.btn_add_author').attr("disabled", "1");
            const getAuthors = function () {
                refreshAuthors();
                $("#form_add_author")[0].reset();
                $("#info-box").removeClass('d-none');
                Toast.fire({
                    icon: 'success',
                    title: 'Author added successfully'
                });
                $('.btn_add_author').removeClass("btn-secondary");
                $('.btn_add_author').addClass("btn-primary");
                $('.btn_add_author').removeAttr("disabled");
            }
            setTimeout(getAuthors, 3000);
        }
    });


    $(".next-step-btn").click(async (ev) => {
        let form = document.getElementById('submission-form');
        let formdata = new FormData(form);
        let journal_id = parseInt($('#journal_id').val());
        let submission_id = parseInt($('#submission_id').val());
        let data = {};
        [...formdata.keys()].forEach(key => {
            let values = formdata.getAll(key);
            data[key] = (values.length > 1) ? values : values.join();
        });
        //console.log(data);
        postData('/ojm/' + journal_id + '/save_progress/' + submission_id, data)
            .then((response) => {
                console.log(response);
                if (response.saved) {
                    $('#submission_id').attr('value', response.id);
                    $('#submission_id_upload').attr('value', response.id);
                } else {
                    // ev.preventDefault();
                    // alert(response.error);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });

    $('.swalDefaultSuccess').click(function () {
        Toast.fire({
            icon: 'success',
            title: 'Submission saved successfully.'
        })
    });

    if($("#example1")){
        $("#example1").DataTable({
            "responsive": true, "lengthChange": false, "autoWidth": false,
            "buttons": [], //"copy", "csv", "excel", "pdf", "print", "colvis"
    
        }).buttons().container().appendTo('#example1_wrapper .col-md-6:eq(0)');

        $("#example1").children('tfoot').remove();
    }
    
    if($('#example2')){
        $('#example2').DataTable({
            "paging": true,
            "lengthChange": false,
            "searching": false,
            "ordering": true,
            "info": true,
            "autoWidth": false,
            "responsive": true,
        });
    }


    $(".form-step-btn").click((ev) => {
        let source = ev.target;
        let step_id = parseInt(source.getAttribute('step_id'));
        console.log("GOT STEP: " + step_id);
        postData('/ojm/submission/step/' + step_id, {
            "journal_id": 1
        }).then((response) => response.json)
            .then((response) => {
                //console.log(response);
                let iframedoc = document.getElementById("form-body-container").contentDocument;
                //console.log(iframedoc);
                let form_body = iframedoc.getElementsByTagName("body")[0];
                //console.log(form_body);
                console.log(response);
                form_body.innerHTML = "<b><u>Hello world</u></b>";
            }).catch((error) => {
                console.error("Error:", error);
            });

        let submission_id = $("#submission_id").val();
        postData("/ojm/get_attachments/" + submission_id, {}).then((res) => {
            console.log(res);
            $("#file_table").empty();
            let table = $("#file_table");
            let header = "<tr><th>Name</th><th>Size</th><th>File type</th></tr>";
            table.append(header);
            for (let i = 0; i < res.data.length; i++) {
                let line = "<tr><td>" + res.data[i].name + "</td><td>" + res.data[i].file_size + " Kb</td><td>" + res.data[i].mimetype + "</td><td><td>\
                    <button id='fd_"+ res.data[i].id + "' class='btn btn-danger'>\
                        <span class='fa fa-trash'></span>\
                    </button>\
                </td></td></tr>";
                table.append(line)
            }
        })
    })


    //check if step 5 form required fields are filled
    $('#baseSubmissionForm').on('submit', function (e) {
        errors = "";

        // let x = $('#article_abstract');
        var elementExists = document.getElementById("article_abstract");
        if (elementExists) {
            let title = $('#article_full_title').summernote('isEmpty') ? '' : $('#article_full_title').summernote('code');
            let abstract = $('#article_abstract').summernote('isEmpty') ? '' : $('#article_abstract').summernote('code');
            let highlight = $('#highlights').summernote('isEmpty') ? '' : $('#highlights').summernote('code');
            let titleOk = title.trim() !== '';
            let abstractOk = abstract.trim() !== '';
            let highlightOk = highlight.trim() !== '';
            if (titleOk && abstractOk && highlightOk) {
                // proceed
            }
            else {
                alert('Required fields can not be empty!');
                e.preventDefault();
            }
        }
    })

    $("#affiliations").change((ev)=>{
        let selection = [];
        let options = document.getElementById('affiliations').options;
        let len = options.length;
        data='',
        i=0;
        while (i<len){
            if (options[i].selected){
                selection.push(options[i].value);
            }
            i++;
        }
        $("#aff").attr("value", JSON.stringify(selection));
    })


    $(".others-reviewer-toggler").click(()=>{
        console.log("Hello world ... xxxx");
        $("#others-reviews").toggleClass("d-none");
    })

    $("#others-reviews-close").click(()=>{
        $("#others-reviews").addClass("d-none");
    })


})

async function postData(url = "", data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            // "Content-Type": "application/json",
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(data)
    });

    return await response.json();
}


function refreshAffiliations() {
    postData("/ojm/get_affiliations/", {}).then((res) => {
        let header = "<tr><th>Document type</th><th>Name</th><th>Size</th><th>Date</th><th></th></tr>";
        let body = ""
        for (let i = 0; i < res.data.length; i++) {
            // let line = "<tr><td class='text-capitalize'>" + res.data[i].tname + "</td>\
            // <td class='text-capitalize'>" + res.data[i].fname + "</td>\
            // <td>" + res.data[i].file_size + " Kb</td>\
            // <td>" + res.data[i].create_date + "</td>\
            // <td>\
            //     <a role='button' tabindex='0' id='"+ res.data[i].id +"' fid='"+res.data[i].id+"' sid='"+submission_id+"' onclick='deleteFile(this)' class='btn btn-primary delete-file-btn'>\
            //         <span class='fa fa-trash'></span>\
            //     </a>\
            // </td>\
            // </tr>";
            // body += line;
        }
        // document.getElementById("file_table").innerHTML = header + body;
    })
}

function refreshFiles() {
    let submission_id = document.getElementById("submission_id_upload").value;
    postData("/ojm/get_attachments/" + submission_id, {}).then((res) => {
        let header = "<tr><th>Document type</th><th>Name</th><th>Size</th><th>Date</th><th></th></tr>";
        let body = ""
        for (let i = 0; i < res.data.length; i++) {
            let line = "<tr><td class='text-capitalize'>" + res.data[i].tname + "</td>\
            <td class='text-capitalize'>" + res.data[i].fname + "</td>\
            <td>" + res.data[i].file_size + " Kb</td>\
            <td>" + res.data[i].create_date + "</td>\
            <td>\
                <a role='button' tabindex='0' id='"+ res.data[i].id + "' fid='" + res.data[i].id + "' sid='" + submission_id + "' onclick='deleteFile(this)' class='btn btn-primary delete-file-btn'>\
                    <span class='fa fa-trash'></span>\
                </a>\
            </td>\
            </tr>";
            body += line;
        }
        document.getElementById("file_table").innerHTML = header + body;
    })
}

function refreshReviewers() {
    let submission_id = document.getElementById("submission_id_upload").value;
    postData("/ojm/get_sreviewers/" + submission_id, {}).then((res) => {
        let header = "<tr><th>Title</th><th>Name</th><th>Email</th><th></th></tr>";
        let body = "";
        for (let i = 0; i < res.data.length; i++) {
            let line = "<tr><td>" + res.data[i].title + "</td><td>"
                + res.data[i].name + "</td><td>"
                + res.data[i].email + "</td>\
                    <td>\
                        <a role='button' tabindex='0' rid='"+ res.data[i].id + "'\
                            class='btn btn-danger delrev' onclick='deleteReviewer(this)'>\
                            <span class='fa fa-trash'></span>\
                        </a>\
                    </td>\
                </tr>";
            body += line;
        }
        document.getElementById("reviewers_table").innerHTML = header + body;
    })
}


function refreshAffs(){
    postData("/ojm/get_affiliations", {}).then((res) => {
        let optionss = "<option value=''>--select author's affiliation--</option>";
        for (let i = 0; i < res.data.length; i++) {
            optionss += "<option value='"+res.data[i].id+"'>"+res.data[i].name +"</option>";
        }
        document.getElementById("affiliations").innerHTML = optionss;
    })
}


function refreshAuthors() {
    let submission_id = document.getElementById("submission_id_upload").value;
    postData("/ojm/get_authors/" + submission_id, {}).then((res) => {
        let header = "<tr><th>#</th><th>Title</th><th>Name</th><th>Email</th><th>Affiliations</th><th></th></tr>";
        let body = "";
        let cauthorSelection = document.getElementById("cauthor");
        cauthorSelection.innerHTML = "";
        for (let i = 0; i < res.data.length; i++) {
            let optionss = "";
            optionss += "<option value='' aid='0'>--</option>"
            for (let j=1; j<=res.data[i].author_ids.length; j++){
                if (j === res.data[i].order){
                    optionss += "<option value='"+j+"' aid='"+res.data[i].author_ids[j]+"' selected='selected'>"+j+"</option>"
                }else{
                    optionss += "<option value='"+j+"' aid='"+res.data[i].author_ids[j]+"'>"+j+"</option>"
                }
            }
            let line = "<tr>\
                <td>\
                    <select class='author_order' name='order_"+res.data[i].id+"' id='author_order_"+res.data[i].id+"' required='true'>\
                        "+optionss+"\
                    </select>\
                </td>\
                <td>\
                    <span>" + res.data[i].title + "<span/>\
                </td>\
                <td>"+ res.data[i].name + "</td>\
                <td>"+ res.data[i].email +"</td>\
                <td>\
                    <span>"+ res.data[i].affiliation_summary +"</span>\
                </td>\
                <td>\
                    <div class='d-flex flex-row flex-wrap justify-content-center align-items-center'\
                        style='gap:0.5em'>\
                        <a role='button' tabindex='0' aid='"+ res.data[i].id + "'\
                            class='btn btn-danger' onclick='deleteAuthor(this);'>\
                            <span class='fa fa-trash'></span>\
                        </a>\
                    </div>\
                </td>\
            </tr>";
            let option = document.createElement("option");
            option.setAttribute("value", res.data[i].id);
            option.innerHTML = res.data[i].name;
            cauthorSelection.appendChild(option);
            body += line;
        }
        document.getElementById("authors_table").innerHTML = header + body;
    })
}


function deleteFile(source) {
    let sid = source.getAttribute("sid");
    let fid = source.getAttribute("fid");
    postData("/ojm/delete_attachment/" + sid + "/" + fid, {});
    const refreshTable = () => {
        refreshFiles();
    }
    setTimeout(refreshTable, 3000);
}


function deleteReviewer(source) {
    if (confirm("Are you sure you want to delete this reviewer?") == true) {
        let rid = source.getAttribute("rid");
        postData("/ojm/delete_reviewer/" + rid, {})
        const refreshTable = () => {
            refreshReviewers();
        }
        setTimeout(refreshTable, 3000);
    } else {
        // do nothing !!!
    }
}


function deleteAuthor(source) {
    if (confirm("Are you sure you want to delete this author?") == true) {
        let aid = source.getAttribute("aid");
        postData("/ojm/delete_author/" + aid, {});
        let cauthorSelection = document.getElementById("cauthor");
        cauthorSelection.innerHTML = "";
        for (let i = 0; i < cauthorSelection.childNodes.length; i++) {
            if (cauthorSelection.childNodes[i].getAttribute("value") == aid) {
                cauthorSelection.removeChild(cauthorSelection.childNodes[i]);
            }
        }
        const refreshTable = () => {
            refreshAuthors();
        }
        setTimeout(refreshTable, 3000);
    } else {
        // do nothing !!!
    }
}


//  summernote
function registerSummernote(element, placeholder, max, callbackMax) {
    $(element).summernote({
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']]
        ],
        placeholder,
        callbacks: {
            onKeydown: function (e) {
                var t = e.currentTarget.innerText;
                if (t.length >= max) {
                    //delete key
                    if (e.keyCode != 8)
                        e.preventDefault();
                    // add other keys ...
                }
            },
            onKeyup: function (e) {
                var t = e.currentTarget.innerText;
                if (typeof callbackMax == 'function') {
                    callbackMax(max - t.length);
                }
            },
            onPaste: function (e) {
                var t = e.currentTarget.innerText;
                var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');
                e.preventDefault();
                var all = t + bufferText;
                document.execCommand('insertText', false, all.trim().substring(0, 400));
                if (typeof callbackMax == 'function') {
                    callbackMax(max - t.length);
                }
            }
        }
    });
}
