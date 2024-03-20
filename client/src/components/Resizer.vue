<script>
export default {
    props: ['id_left', 'id_right'],
    data() {
        return {
            left_percent: 30,
        }
    },
    methods: {
        handleMouseDown(event) {
            event.preventDefault();
            event.stopPropagation();

            document.addEventListener('mousemove', this.handleMouseMove);
            document.addEventListener('mouseup', this.handleMouseUp);
        },
        handleMouseMove(event) {
            const container_element= document.querySelector('.resizer-container');
            let leftWidth = event.clientX - container_element.getBoundingClientRect().left;
            // if (leftWidth < 240) leftWidth = 240;
            // if (container_element.clientWidth - leftWidth < 240) leftWidth = container_element.clientWidth - 240;

            this.left_percent = leftWidth / container_element.clientWidth * 100;
        },
        handleMouseUp() {
            document.removeEventListener('mousemove', this.handleMouseMove);
            document.removeEventListener('mouseup', this.handleMouseUp);
        },

    }


}
</script>

<template>
    <div class="resizer-container">
        <div id="resizer-left" class="resizer" :style="{width:left_percent+'%'}">
            <slot name="left"/>
        </div>
        <div id="middle-line" :style="{left:left_percent+'%'}" @mousedown="handleMouseDown" >
        </div>
        <div id="resizer-right" class="resizer" :style="{width:100-left_percent+'%-3px'}">
            <slot name="right"/>
        </div>
    </div>

</template>

<style scoped>
.resizer-container {
    top:2.5vh;
    left:2.5vw;
    width: 95vw;
    height: 95vh;
    position: absolute;
}
#resizer-left {
    position: absolute;
    width: 50%;
    height: 100%;
    top: 0;
    left: 0;
    /* background-color: #f0f0f0; */
    z-index: 100;
}
#middle-line {
    position: absolute;
    width: 3px;
    height: 100%;
    top: 0;
    left: 50%;
    background-color: #000;
    z-index: 100;
}
#middle-line:hover {
    cursor: ew-resize;
}

#resizer-right {
    position: absolute;
    width: 50%;
    height: 100%;
    top: 0;
    right: 0;
    /* background-color: #f0f0f0; */
    z-index: 100;
}
</style>