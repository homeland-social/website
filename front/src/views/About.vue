<template>
  <v-main>
    <v-container fluid>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md6>
          <p class="text-h5">homeland.social is a new type of social network</p>
          <p>Social networks are never free. Users of social media willingly trade privacy, autonomy and information access in order to communicate with others.</p>
          <p>While home broadband, powerful computers and wifi have made it easer than ever to host your own website, there remain technical hurdles to doing so.</p>
          <p>homeland.social provides easy to use solutions for DNS, uPnP, SSL certificates and much more. We allow anyone to take advantage of the technology they already own.</p>
          <v-list three-line>
            <v-list-item>
              <v-list-item-icon>
                <v-img src="@/assets/wifi-router.png"></v-img>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Use what you have</v-list-item-title>
                <v-list-item-subtitle>
                  Use your home Internet access to self-host a own social network
                  Share with your friends, family, neigbors, or the world.
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>Works globally</v-list-item-title>
                <v-list-item-subtitle>Social networking sites on the federverse, including all those using homeland.social are "federated" with one another to create one large social network.</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-icon>
                <v-img src="@/assets/connected-globe.png"></v-img>
              </v-list-item-icon>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-img src="@/assets/lock.png"></v-img>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Ultimate privacy</v-list-item-title>
                <v-list-item-subtitle>
                  Maintain firm control over your privacy by ensuring your data is not shared
                  unless you share it. Every aspect is user-controlled and each option provides
                  documentation about how privacy is affected.
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>
