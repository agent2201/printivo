<?php
/**
 * Plugin Name: NEXUS Uploader (Pro Calculator Edition)
 * Version: 3.0.0
 * Description: Custom file uploader with tiered pricing, base64 cart previews, and WordPress image proxy.
 */

if ( ! defined( 'ABSPATH' ) ) exit;

define( 'NEXUS_TUNNEL_URL', 'https://uncontending-mitch-ungarrisoned.ngrok-free.dev' );

class Nexus_Uploader {
    public function __construct() {
        add_action( 'init', array( $this, 'register_nexus_endpoint' ) );
        add_filter( 'query_vars', array( $this, 'add_nexus_query_vars' ) );
        add_filter( 'woocommerce_account_menu_items', array( $this, 'add_nexus_link_my_account' ) );
        add_action( 'woocommerce_account_nexus-designs_endpoint', array( $this, 'nexus_designs_content' ) );

        add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_nexus_assets' ) );
        add_action( 'woocommerce_before_add_to_cart_button', array( $this, 'render_uploader_ui' ) );
        
        // Cart Logic
        add_filter( 'woocommerce_add_cart_item_data', array( $this, 'add_nexus_file_to_cart' ), 10, 3 );
        add_filter( 'woocommerce_get_item_data', array( $this, 'display_nexus_file_in_cart' ), 10, 2 );
        add_filter( 'woocommerce_cart_item_thumbnail', array( $this, 'replace_cart_thumbnail' ), 10, 3 );
        add_action( 'woocommerce_checkout_create_order_line_item', array( $this, 'save_nexus_file_to_order' ), 10, 4 );
        
        // Dynamic Pricing Logic (The "Calculator")
        add_action( 'woocommerce_before_calculate_totals', array( $this, 'apply_custom_dynamic_price' ), 10, 1 );

        add_action( 'woocommerce_thankyou', array( $this, 'frontend_notify_nexus' ), 10, 1 );

        add_action( 'init', array( $this, 'fix_site_settings' ) );
        // Скрываем DTF Gang Sheet из всех меню
        add_filter( 'wp_nav_menu_objects', array( $this, 'hide_gang_sheet_menu' ), 99, 2 );

        // REST API: Image Proxy (Solution A)
        add_action( 'rest_api_init', array( $this, 'register_image_proxy_route' ) );
    }

    // ============================================================
    // A) REST API Image Proxy — serves MinIO images through WordPress domain
    // ============================================================
    public function register_image_proxy_route() {
        register_rest_route( 'nexus/v1', '/image/(?P<path>.+)', array(
            'methods'  => 'GET',
            'callback' => array( $this, 'proxy_image_handler' ),
            'permission_callback' => '__return_true',
        ));
    }

    public function proxy_image_handler( $request ) {
        $path = $request->get_param( 'path' );
        // Allow slashes in path for subfolders like thumbnails/ or originals/
        $path = str_replace( '../', '', $path ); 

        $remote_url = NEXUS_TUNNEL_URL . '/nexus-uploads/' . $path;

        $response = wp_remote_get( $remote_url, array(
            'timeout' => 15,
            'headers' => array( 'ngrok-skip-browser-warning' => 'true' ),
        ));

        if ( is_wp_error( $response ) ) {
            return new WP_REST_Response( 'Image fetch failed', 502 );
        }

        $body = wp_remote_retrieve_body( $response );
        $content_type = wp_remote_retrieve_header( $response, 'content-type' );

        if ( empty( $content_type ) || strpos( $content_type, 'text/html' ) !== false ) {
            $content_type = 'image/png';
        }

        header( 'Content-Type: ' . $content_type );
        header( 'Cache-Control: public, max-age=86400' );
        header( 'Content-Length: ' . strlen( $body ) );
        echo $body;
        exit;
    }

    /**
     * Build a proxy URL for an image.
     * Original key format: 'nexus-uploads/thumbnails/filename.jpg'
     */
    private function proxy_url( $key ) {
        // Remove bucket name from the start if present
        $path = str_replace( 'nexus-uploads/', '', $key );
        return rest_url( 'nexus/v1/image/' . $path );
    }

    // ============================================================
    // Menu & Settings
    // ============================================================
    public function hide_gang_sheet_menu( $items, $args ) {
        foreach ( $items as $key => $item ) {
            if ( stripos( $item->title, 'gang sheet' ) !== false ) {
                unset( $items[$key] );
            }
        }
        return $items;
    }

    public function fix_site_settings() {
        if ( isset($_SERVER['HTTP_HOST']) && $_SERVER['HTTP_HOST'] !== 'test8.newsite.co.ua' ) return;
        update_option( 'users_can_register', 1 );
        update_option( 'woocommerce_enable_myaccount_registration', 'yes' );
    }

    // ============================================================
    // Dynamic Pricing Engine
    // ============================================================
    public function apply_custom_dynamic_price( $cart ) {
        if ( is_admin() && ! defined( 'DOING_AJAX' ) ) return;

        foreach ( $cart->get_cart() as $cart_item_key => $cart_item ) {
            if ( isset( $cart_item['nexus_file_path'] ) ) {
                $custom_price = $this->calculate_nexus_total_price( $cart_item['nexus_file_path'] );
                if ( $custom_price > 0 ) {
                    $cart_item['data']->set_price( $custom_price );
                }
            }
        }
    }

    private function calculate_nexus_total_price( $raw_data ) {
        $files = json_decode( $raw_data, true );
        if ( ! is_array( $files ) ) return 0;

        $total_sq_cm = 0;
        foreach ( $files as $f ) {
            $w = isset($f['width']) ? floatval($f['width']) : 30;
            $h = isset($f['height']) ? floatval($f['height']) : 30;
            $q = isset($f['qty']) ? intval($f['qty']) : 1;
            $total_sq_cm += ($w * $h * $q);
        }

        $total_sq_in = $total_sq_cm / 6.4516;
        
        // Tiered logic per your specific rates
        $rate = 0.060;
        if ( $total_sq_in >= 3000 ) $rate = 0.017;
        elseif ( $total_sq_in >= 1600 ) $rate = 0.020;
        elseif ( $total_sq_in >= 700 ) $rate = 0.022;
        elseif ( $total_sq_in >= 20 ) $rate = 0.030;

        return round( $total_sq_in * $rate, 2 );
    }

    // ============================================================
    // UI Rendering
    // ============================================================
    public function render_uploader_ui() {
        ?>
        <div id="nexus-uploader-container" class="nexus-uploader">
            <label><strong><?php echo $this->nt('Charger vos fichiers (PNG, SVG):', 'Upload your files (PNG, SVG):'); ?></strong></label>
            <div class="nexus-dropzone" id="nexus-dropzone">
                <span id="nexus-status-text"><?php echo $this->nt('Glissez-déposez здесь или Cliquez', 'Drag & Drop here or Click'); ?></span>
                <input type="file" id="nexus-upload-input" multiple style="display:none;" accept="image/png,image/svg+xml">
                <div id="nexus-progress-bar" style="display:none;"><div id="nexus-progress-inner"></div></div>
            </div>

            <div id="nexus-files-table-container" style="display:none; margin-top:20px;">
                <table class="nexus-table" style="width:100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="border-bottom:1px solid #eee;">
                            <th>Fichier</th> <th>Dimensions (cm)</th> <th>Qty</th> <th></th>
                        </tr>
                    </thead>
                    <tbody id="nexus-files-list"></tbody>
                </table>
                <div style="margin-top:15px; padding:10px; background:#f9f9f9; border-radius:8px; text-align:right;">
                    <strong><?php echo $this->nt('Total Surface:', 'Total Area:'); ?></strong> <span id="nexus-total-area">0</span> см² 
                    <br>
                    <strong style="color:#FF0080; font-size:1.2em;"><?php echo $this->nt('Prix Estimé:', 'Estimated Price:'); ?> $<span id="nexus-total-price-val">0.00</span></strong>
                </div>
            </div>

            <input type="hidden" name="nexus_file_path" id="nexus-file-path-hidden">
        </div>
        <?php
    }

    private function nt($fr, $en) { return (strpos(get_locale(), 'fr') === 0) ? $fr : $en; }

    public function enqueue_nexus_assets() {
        wp_enqueue_style( 'nexus-uploader-css', plugin_dir_url( __FILE__ ) . 'assets/nexus-style.css', array(), '3.0.1' );
        wp_enqueue_script( 'nexus-uploader-js', plugin_dir_url( __FILE__ ) . 'assets/nexus-uploader.js', array('jquery'), '3.0.1', true );
        wp_localize_script( 'nexus-uploader-js', 'nexus_config', array(
            'endpoint' => NEXUS_TUNNEL_URL,
            'isFr'     => (strpos(get_locale(), 'fr') === 0)
        ));
    }

    // ============================================================
    // My Account: NEXUS Designs (Solution A — proxy URLs)
    // ============================================================
    public function register_nexus_endpoint() { add_rewrite_endpoint( 'nexus-designs', EP_ROOT | EP_PAGES ); }
    public function add_nexus_query_vars( $vars ) { $vars[] = 'nexus-designs'; return $vars; }
    public function add_nexus_link_my_account( $items ) {
        $new_items = array();
        foreach ( $items as $key => $value ) {
            $new_items[$key] = $value;
            if ( 'dashboard' === $key ) { $new_items['nexus-designs'] = $this->nt('Mes Designs', 'My Designs'); }
        }
        return $new_items;
    }

    public function nexus_designs_content() {
        echo '<h3>🎨 ' . $this->nt('Mes Designs NEXUS', 'My NEXUS Designs') . '</h3>';
        $customer_orders = get_posts( array('numberposts' => -1, 'meta_key' => '_customer_user', 'meta_value' => get_current_user_id(), 'post_type' => wc_get_order_types(), 'post_status' => array_keys( wc_get_order_statuses() )) );
        if ( ! $customer_orders ) { echo '<p>' . $this->nt('Aucun design trouvé.', 'No designs found.') . '</p>'; return; }
        echo '<table class="shop_table my_account_orders"><thead><tr><th>' . $this->nt('Commande', 'Order') . '</th><th>Design</th><th>' . $this->nt('Fichier', 'File') . '</th><th>Dimensions</th><th>Action</th></tr></thead><tbody>';
        foreach ( $customer_orders as $customer_order ) {
            $order = wc_get_order( $customer_order->ID );
            foreach ( $order->get_items() as $item ) {
                $raw_data = $item->get_meta( 'nexus_file_path' );
                if ( $raw_data ) {
                    $files = json_decode( $raw_data, true );
                    if(is_array($files)) {
                        foreach ($files as $f) {
                            $thumb_key = !empty($f['thumb_key']) ? $f['thumb_key'] : $f['key'];
                            $img_url = $this->proxy_url( $thumb_key );
                            $dl_url  = NEXUS_TUNNEL_URL . '/' . $f['key'];
                            echo '<tr>
                                <td>#' . esc_html($order->get_order_number()) . '</td>
                                <td><img src="' . esc_attr($img_url) . '" style="width:60px; height:60px; object-fit:contain; border-radius:5px; background:#f5f5f5;" /></td>
                                <td>' . esc_html($f['name']) . '</td>
                                <td>' . esc_html($f['width']) . 'x' . esc_html($f['height']) . 'cm x' . esc_html($f['qty']) . '</td>
                                <td><a href="' . esc_attr($dl_url) . '" class="button" target="_blank" style="background:#FF0080; color:white;">Download</a></td>
                            </tr>';
                        }
                    }
                }
            }
        }
        echo '</tbody></table>';
    }

    // ============================================================
    // Cart: Add to Cart (preserve JSON + base64 thumb)
    // ============================================================
    public function add_nexus_file_to_cart( $cart_item_data, $product_id, $variation_id ) {
        if ( isset( $_POST['nexus_file_path'] ) && ! empty( $_POST['nexus_file_path'] ) ) {
            $raw = wp_unslash( $_POST['nexus_file_path'] );
            $decoded = json_decode( $raw, true );
            if ( is_array( $decoded ) ) {
                // Store the full data (includes 'thumb' base64 from JS)
                $cart_item_data['nexus_file_path'] = json_encode( $decoded );
                $cart_item_data['unique_key'] = md5( microtime() . rand() );
            }
        }
        return $cart_item_data;
    }

    // ============================================================
    // Cart: Display file info
    // ============================================================
    public function display_nexus_file_in_cart( $item_data, $cart_item ) {
        if ( isset( $cart_item['nexus_file_path'] ) ) {
            $files = json_decode( $cart_item['nexus_file_path'], true );
            if ( is_array($files) ) {
                foreach ($files as $i => $f) {
                    $item_data[] = array(
                        'name' => $this->nt('Fichier', 'File') . ' ' . ($i + 1),
                        'value' => esc_html($f['name']) . ' (' . esc_html($f['width']) . 'x' . esc_html($f['height']) . 'cm, Qty: ' . esc_html($f['qty']) . ')'
                    );
                }
            }
        }
        return $item_data;
    }

    // ============================================================
    // Cart: Replace thumbnail with base64 preview (Solution B)
    // ============================================================
    public function replace_cart_thumbnail( $thumbnail, $cart_item, $cart_item_key ) {
        if ( isset( $cart_item['nexus_file_path'] ) ) {
            $files = json_decode( $cart_item['nexus_file_path'], true );
            if ( is_array($files) && count($files) > 0 && ! empty($files[0]['thumb']) ) {
                $thumb = $files[0]['thumb'];
                // Validate that it's actually a data URI (security check)
                if ( strpos($thumb, 'data:image/') === 0 ) {
                    return '<img src="' . esc_attr($thumb) . '" alt="' . esc_attr($files[0]['name']) . '" style="width:90px; height:90px; object-fit:contain; border-radius:5px; background:#f9f9f9;" />';
                }
            }
            // Fallback: use proxy URL of the thumbnail
            if ( is_array($files) && count($files) > 0 ) {
                $f = $files[0];
                $thumb_key = !empty($f['thumb_key']) ? $f['thumb_key'] : $f['key'];
                $proxy = $this->proxy_url( $thumb_key );
                return '<img src="' . esc_attr($proxy) . '" alt="NEXUS Design" style="width:90px; height:90px; object-fit:contain; border-radius:5px; background:#f9f9f9;" />';
            }
        }
        return $thumbnail;
    }

    // ============================================================
    // Checkout: Save meta to order
    // ============================================================
    public function save_nexus_file_to_order( $item, $cart_item_key, $values, $order ) {
        if ( isset( $values['nexus_file_path'] ) ) {
            // Strip base64 thumbs before saving to order meta (save space)
            $files = json_decode( $values['nexus_file_path'], true );
            if ( is_array( $files ) ) {
                foreach ( $files as &$f ) {
                    unset( $f['thumb'] ); // Remove thumb from order storage
                }
                $item->add_meta_data( 'nexus_file_path', json_encode( $files ), true );
            } else {
                $item->add_meta_data( 'nexus_file_path', $values['nexus_file_path'], true );
            }
        }
    }

    // ============================================================
    // Checkout: Notify NEXUS API (Via Frontend JS)
    // ============================================================
    public function frontend_notify_nexus( $order_id ) {
        if ( ! $order_id ) return;
        $order = wc_get_order( $order_id );
        
        $customer_name = $order->get_billing_first_name() . ' ' . $order->get_billing_last_name();
        $payloads = array();

        foreach ( $order->get_items() as $item ) {
            $file_path = $item->get_meta( 'nexus_file_path' );
            if ( $file_path ) {
                $payloads[] = array(
                    'order_id'  => $order_id,
                    'file_path' => $file_path,
                    'customer'  => $customer_name,
                    'quantity'  => $item->get_quantity(),
                    'product'   => $item->get_name(),
                );
            }
        }

        if ( empty( $payloads ) ) return;

        // Print JS to send the data directly from the user's browser to the Ngrok tunnel
        ?>
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            var payloads = <?php echo json_encode( $payloads ); ?>;
            var tunnelUrl = "<?php echo esc_js( NEXUS_TUNNEL_URL ); ?>";
            
            payloads.forEach(function(payload) {
                fetch(tunnelUrl + '/api/order/callback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ngrok-skip-browser-warning': 'true'
                    },
                    body: JSON.stringify(payload)
                }).then(r => console.log('NEXUS sync OK'))
                  .catch(e => console.error('NEXUS sync err', e));
            });
        });
        </script>
        <?php
    }
}

new Nexus_Uploader();
