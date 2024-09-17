const imageUploader = document.querySelector("input");
const imagePreview = document.querySelector("img");

function showImage() {
    let reader = new FileReader();
    reader.readAsDataURL(imageUploader.files[0]);
    reader.onload = function (e) {
        imagePreview.classList.add("show");
        imagePreview.src = e.target.result;
    };
}

// OR

// function showImage() {
//   const file = imageUploader.files[0];
//     imagePreview.classList.add("show");
//     imagePreview.src = URL.createObjectURL(file);
// }