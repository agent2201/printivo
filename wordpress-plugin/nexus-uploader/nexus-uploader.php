<?php
/**
 * Plugin Name: NEXUS Printivo Uploader
 * Description: Загрузчик файлов напрямую на локальный сервер NEXUS (вместо Kixxl).
 * Version: 1.0.0
 * Author: NEXUS
 */

if ( ! defined( 'ABSPATH' ) ) exit;

class Nexus_Uploader {

    public function __construct() {
        // Добавление интерфейса загрузки на страницу товара
        add_action( 'woocommerce_before_add_to_cart_button', array( $this, 'render_uploader_ui' ) );
        
        // Сохранение ссылки на файл в метаданных корзины
        add_filter( 'woocommerce_add_cart_item_data', array( $this, 'add_nexus_file_to_cart' ), 10, 3 );
        
        // Отображение ссылки в корзине и при оформлении заказа
        add_filter( 'woocommerce_get_item_data', array( $this, 'display_nexus_file_in_cart' ), 10, 2 );
        
        // Сохранение ссылки в метаданные заказа
        add_action( 'woocommerce_checkout_create_order_line_item', array( $this, 'save_nexus_file_to_order' ), 10, 4 );

        // Скрытие Kixxl через CSS (если он активен)
        add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_nexus_assets' ) );

        // --- Личный кабинет NEXUS ---
        add_action( 'init', array( $this, 'add_nexus_endpoint' ) );
        add_filter( 'query_vars', array( $this, 'nexus_query_vars' ), 0 );
        add_filter( 'woocommerce_account_menu_items', array( $this, 'add_nexus_link_my_account' ) );
        add_action( 'woocommerce_account_nexus-designs_endpoint', array( $this, 'nexus_designs_content' ) );

        // Автоматическое создание точки входа (Страницы и Кнопки в меню)
        add_action( 'init', array( $this, 'setup_nexus_account_entry_point' ) );
    }

    public function enqueue_nexus_assets() {
        wp_enqueue_style( 'nexus-uploader-css', plugin_dir_url( __FILE__ ) . 'assets/nexus-style.css', array(), time() );
        wp_enqueue_script( 'nexus-uploader-js', plugin_dir_url( __FILE__ ) . 'assets/nexus-uploader.js', array('jquery'), time(), true );
        
        // Передача настроек туннеля в JS
        wp_localize_script( 'nexus-uploader-js', 'nexus_config', array(
            'endpoint' => 'https://uncontending-mitch-ungarrisoned.ngrok-free.dev',
            'bucket'   => 'nexus-uploads'
        ));
    }

    public function render_uploader_ui() {
        ?>
        <div id="nexus-uploader-container" class="nexus-uploader">
            <label for="nexus-upload-input">Загрузить файлы (PNG, SVG):</label>
            <div class="nexus-dropzone" id="nexus-dropzone">
                <span id="nexus-status-text">Перетащите файлы сюда или нажмите для выбора</span>
                <input type="file" id="nexus-upload-input" multiple style="display:none;" accept="image/png,image/svg+xml">
                <div id="nexus-progress-bar" style="display:none;">
                    <div id="nexus-progress-inner"></div>
                </div>
            </div>
            <input type="hidden" name="nexus_file_path" id="nexus-file-path-hidden">
            <input type="hidden" name="nexus_file_preview" id="nexus-file-preview-hidden">
        </div>
        <style>
            .nexus-uploader { margin-bottom: 20px; border: 2px dashed #0073aa; padding: 20px; text-align: center; border-radius: 8px; }
            #nexus-progress-bar { width: 100%; background: #eee; height: 10px; margin-top: 10px; border-radius: 5px; overflow: hidden; }
            #nexus-progress-inner { height: 100%; background: #0073aa; width: 0%; transition: width 0.3s; }
            /* Возвращаем стандартную кнопку покупки, которую мог скрыть Kixxl */
            .single_add_to_cart_button { display: inline-block !important; visibility: visible !important; }
            #kixxl-custom-button { display: none !important; }
        </style>
        <?php
    }

    public function add_nexus_file_to_cart( $cart_item_data, $product_id, $variation_id ) {
        if ( isset( $_POST['nexus_file_path'] ) && ! empty( $_POST['nexus_file_path'] ) ) {
            $cart_item_data['nexus_file_path'] = sanitize_text_field( $_POST['nexus_file_path'] );
            if ( isset( $_POST['nexus_file_preview'] ) ) {
                $cart_item_data['nexus_file_preview'] = sanitize_text_field( $_POST['nexus_file_preview'] );
            }
        }
        return $cart_item_data;
    }

    public function display_nexus_file_in_cart( $item_data, $cart_item ) {
        if ( isset( $cart_item['nexus_file_path'] ) ) {
            $item_data[] = array(
                'name' => 'NEXUS File',
                'value' => '✔ Загружено (ID: ' . basename($cart_item['nexus_file_path']) . ')'
            );
        }
        return $item_data;
    }

    public function save_nexus_file_to_order( $item, $cart_item_key, $values, $order ) {
        if ( isset( $values['nexus_file_path'] ) ) {
            $item->add_meta_data( 'nexus_file_path', $values['nexus_file_path'] );
        }
    }

    // --- Методы личного кабинета NEXUS ---

    public function add_nexus_endpoint() {
        add_rewrite_endpoint( 'nexus-designs', EP_ROOT | EP_PAGES );
        
        // Автоматический сброс кэша ссылок (один раз)
        if ( ! get_option( 'nexus_rules_flushed_v1' ) ) {
            flush_rewrite_rules( false );
            update_option( 'nexus_rules_flushed_v1', true );
        }
    }

    public function setup_nexus_account_entry_point() {
        if ( get_option( 'nexus_entry_point_created_v1' ) || ! function_exists('wc_get_page_id') ) {
            return;
        }

        $page_title = 'Личный кабинет NEXUS';
        $page_content = '[woocommerce_my_account]';
        $page_id = wc_get_page_id( 'myaccount' );

        // 1. Создаем страницу, если её физически не существует
        if ( $page_id <= 0 ) {
            $page_check = get_page_by_title( $page_title );
            if ( isset( $page_check->ID ) ) {
                $page_id = $page_check->ID;
            } else {
                $page_id = wp_insert_post( array(
                    'post_title'   => $page_title,
                    'post_content' => $page_content,
                    'post_status'  => 'publish',
                    'post_type'    => 'page',
                ) );
            }
            if ( $page_id ) {
                update_option( 'woocommerce_myaccount_page_id', $page_id );
            }
        }

        // 2. Автоматически выводим кнопку в главное меню сайта
        $menus = wp_get_nav_menus();
        if ( ! empty( $menus ) && $page_id ) {
            $menu_id = $menus[0]->term_id; // Берем первое активное меню
            
            $menu_items = wp_get_nav_menu_items( $menu_id );
            $exists = false;
            
            if ( $menu_items ) {
                foreach ( $menu_items as $item ) {
                    if ( $item->object_id == $page_id ) {
                        $exists = true;
                        break;
                    }
                }
            }

            // Если кнопки еще нет в меню - добавляем её
            if ( ! $exists ) {
                wp_update_nav_menu_item( $menu_id, 0, array(
                    'menu-item-title'     => 'Мой Кабинет',
                    'menu-item-object-id' => $page_id,
                    'menu-item-object'    => 'page',
                    'menu-item-status'    => 'publish',
                    'menu-item-type'      => 'post_type',
                ) );
            }
        }

        update_option( 'nexus_entry_point_created_v1', true ); // Ставим флаг, чтобы больше не запускать
    }

    public function nexus_query_vars( $vars ) {
        $vars[] = 'nexus-designs';
        return $vars;
    }

    public function add_nexus_link_my_account( $items ) {
        // Вставляем вкладку "Мои Макеты" перед "Выход" (logout)
        $new_items = array();
        foreach ( $items as $key => $value ) {
            if ( $key === 'customer-logout' ) {
                $new_items['nexus-designs'] = 'Мои Макеты';
            }
            $new_items[$key] = $value;
        }
        return $new_items;
    }

    public function nexus_designs_content() {
        echo '<h3>🎨 Мои макеты NEXUS</h3>';
        echo '<p>Здесь безопасно хранятся исходники всех ваших заказов. Файлы лежат на локальном высокоскоростном сервере типографии.</p>';
        
        $customer_orders = get_posts( array(
            'numberposts' => -1,
            'meta_key'    => '_customer_user',
            'meta_value'  => get_current_user_id(),
            'post_type'   => wc_get_order_types(),
            'post_status' => array_keys( wc_get_order_statuses() ),
        ) );

        if ( ! $customer_orders ) {
            echo '<div class="woocommerce-message">У вас еще нет заказов с загруженными макетами.</div>';
            return;
        }

        echo '<table class="woocommerce-orders-table woocommerce-MyAccount-orders shop_table shop_table_responsive my_account_orders account-orders-table">';
        echo '<thead><tr><th class="order-number">Заказ</th><th class="order-date">Дата</th><th class="order-total">Файл</th><th class="order-actions">Действие</th></tr></thead><tbody>';

        $has_files = false;

        foreach ( $customer_orders as $customer_order ) {
            $order = wc_get_order( $customer_order->ID );
            $items = $order->get_items();
            
            foreach ( $items as $item_id => $item ) {
                $nexus_path = $item->get_meta( 'nexus_file_path' );
                if ( ! empty( $nexus_path ) ) {
                    $has_files = true;
                    $order_url = $order->get_view_order_url();
                    // Формируем ссылку на ваш локальный сервер MinIO
                    $download_url = 'https://uncontending-mitch-ungarrisoned.ngrok-free.dev/' . esc_attr($nexus_path);
                    
                    echo '<tr class="woocommerce-orders-table__row">';
                    echo '<td class="woocommerce-orders-table__cell" data-title="Заказ"><a href="' . esc_url($order_url) . '">#' . $order->get_order_number() . '</a></td>';
                    echo '<td class="woocommerce-orders-table__cell" data-title="Дата">' . wc_format_datetime( $order->get_date_created() ) . '</td>';
                    echo '<td class="woocommerce-orders-table__cell" data-title="Файл"><strong>' . basename($nexus_path) . '</strong></td>';
                    echo '<td class="woocommerce-orders-table__cell" data-title="Действие"><a href="' . esc_url($download_url) . '" target="_blank" class="woocommerce-button button view" style="background:#FF0080; color:white;">Скачать оригинал</a></td>';
                    echo '</tr>';
                }
            }
        }

        if ( ! $has_files ) {
            echo '<tr><td colspan="4">В ваших текущих заказах макетов не найдено.</td></tr>';
        }

        echo '</tbody></table>';
    }
}

new Nexus_Uploader();
