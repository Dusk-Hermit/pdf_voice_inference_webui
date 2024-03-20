<script>
import PDFViewer from './PDFViewer.vue';
import Controls from './Controls.vue';
// import Resizer from './Resizer.vue';
export default {
    components: {
        PDFViewer,
        Controls,
        // Resizer,
    }
}

</script>

<template>
    <div class="pdf-container">
        <div class="left">
            <Controls />
        </div>
        <div class="right">
            <PDFViewer id="pdfviewer" :url="'http://localhost:5001/pdf'" />
        </div>
    </div>
</template>

<style scoped>
.pdf-container {
    width: 100%;
    height: 100%;
}

.left {
    width: 30%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    /* background-color: #f0f0f0; */
    /* z-index: 100; */
}

.right {
    width: 70%;
    height: 100%;
    position: absolute;
    top: 0;
    right: 0;
    /* background-color: #f0f0f0; */
    /* z-index: 100; */
}
</style>