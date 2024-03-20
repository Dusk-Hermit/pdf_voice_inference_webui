<template>
	<div class="container">
		<iframe :src="pdfUrl" id="pdf-iframe" width="100%" height="100%"></iframe>
	</div>
</template>

<script >
// import { defineProps, ref, onMounted } from 'vue';

export default {
	props: ['url'],
	data() {
		return {
			pdfUrl: '',
		};
	},
	methods:{
		set_pdf_url(url){
			const fileUrl = '/pdfjs-4.0.379-dist/web/viewer.html?file='
			this.pdfUrl = fileUrl + encodeURIComponent(url)
			// console.log(this.pdfUrl)
			// console.log(url)
		},
	},
	created() {
		console.log(this.url)
		this.set_pdf_url(this.url)
	},

};
</script>

<style scoped>
.container {
	width: 100%;
	height: 100%;
}
</style>