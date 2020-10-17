<template>
  <div justify="center" v-if="Dialog">
    <v-dialog v-model="Dialog" max-width="1200px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">{{
            cardData.operation.name
          }}</span>
        </v-card-title>
        <v-row class="mx-3">
          <v-col cols="5">
            <v-img
              max-height="600"
              max-width="600"
              :src="cardData.operation.image"
            >
            </v-img>
          </v-col>
          <v-col cols="4">
            <v-card-text class="pa-0">
              <v-list-item three-line>
                <v-list-item-content>
                  <div class="overline mb-4">{{ cardData.name }}</div>
                  <v-textarea
                    label="Operation Description"
                    auto-grow
                    outlined
                    rows="3"
                    row-height="25"
                    disabled
                    v-model="cardData.operation.description"
                    shaped>
                  </v-textarea>
                  <v-list-item-subtitle>
                    QTY: {{ cardData.for_quantity }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle>
                    Production Item: {{ cardData.production_item }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle>
                    Satus: {{ cardData.status }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-card-text>
          </v-col>
          <v-col cols="3">
            <v-img
              max-height="400"
              max-width="400"
              :src="cardData.work_order_image"
            >
            </v-img>
          </v-col>
        </v-row>
        <v-card-actions class="mx-3">
          <v-btn color="primary" dark @click="close_dialog">Start</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from "./bus";
export default {
  data: () => ({
    Dialog: false,
    cardData: "",
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.Dialog = false;
    },
  },
  created: function () {
    evntBus.$on("open_card", (job_card) => {
      this.Dialog = true;
      this.cardData = job_card;
    });
  },
};
</script>