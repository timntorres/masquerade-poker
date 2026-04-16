<script lang="ts">
    import CardContainer from "./CardContainer.svelte";
    import type { Card } from "./interfaces";

    let { community_cards, pot }: { community_cards:Array<Card>, pot: number } = $props();
        
</script>

    <div class="container">
        <!-- Seat 1 -->
        <div class="betlocation a">
            <div class="bet">
                $0.00
            </div>
        </div>
        <div class="btnlocation b">
            B
        </div>

        <!-- Seat 2 -->
        <div class="btnlocation c">
            B
        </div>
        <div class="betlocation d">
            <div class="bet">
                $0.00
            </div>
        </div>

        <!-- Seat 3 -->
        <div class="btnlocation e">
            B
        </div>
        <div class="betlocation f">
            <div class="bet">
                $0.00
            </div>
        </div>
        
        <!-- Seat 4 -->
        <div class="btnlocation g">
            B
        </div>
        <div class="betlocation h">
            <div class="bet">
                $0.00
            </div>
        </div>

        <!-- Seat 5 -->
        <div class="betlocation rightalign i">
            <div class="bet">
                $0.00
            </div>
        </div>
        <div class="btnlocation j">
            B
        </div>

        <!-- Seat 6 -->
        <div class="btnlocation k">
            B
        </div>
        <div class="betlocation rightalign l">
            <div class="bet">
                $0.00
            </div>
        </div>
        

        <div class= "board center">
            <CardContainer cards={community_cards} />
            <div class= "pot center">
                ${pot.toFixed(2)}
            </div>
        </div>

    </div>

<style>

    .center {
        grid-area: 2 / 2 / 11 / 12;
    }

    .l {
        grid-area: 6 / 12 / 7 / 13;
    }

    .k {
        grid-area: 5 / 12 / 6 / 13;
    }


    .j {
        grid-area: 3 / 12 / 4 / 13;
    }

    .i {
        grid-area: 2 / 12 / 3 / 13;
    }


    .h {
        grid-area: 1 / 10 / 2 / 11;
    }

    .g {
        grid-area: 1 / 9 / 2 / 10;
    }


    .f {
        grid-area: 1 / 4 / 2 / 5;
    }

    .e {
        grid-area: 1 / 3 / 2 / 4;
    }


    .d {
        grid-area: 2 / 1 / 3 / 2;
    }

    .c {
        grid-area: 3 / 1 / 4 / 2;
    }


    .b {
        grid-area: 5 / 1 / 6 / 2;
    }

    .a {
        grid-area: 6 / 1 / 7 / 2;
    }

    .bet {
        position:absolute;
        font-family: 'Apple SD Gothic Neo';
        font-size: 2cqw;
        font-weight: 200;
        letter-spacing: -.15cqw;
    }

    .betlocation {
        position:relative;
    }

    .btnlocation {
        background-image: linear-gradient(white, lightgray);
        border-style: solid;
        border-width: 0.5cqw;
        justify-content: center;
        text-align: center;

        box-sizing: border-box;
        width: 3cqw;
        height: 3cqw;
        border-radius: 50%;
        border-color: white;
        color: darkslategray;
        font-family: 'Apple SD Gothic Neo';
        font-size: 2cqw;
        font-weight: 900;
    }

    .container {
      display: grid;
      width: 100%;
      grid-template-columns: repeat(12, 1fr);
      grid-template-rows: repeat(6, 1fr);
    }

    .board {
        margin-left: 2.5cqw;

    }

    .pot {
        position:absolute;
        margin-top: 27cqh;
        margin-left: 12cqw;

        font-size: 3cqw;
        font-family: 'Apple SD Gothic Neo';
        font-weight: 500;

    }

    .rightalign {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }



</style>